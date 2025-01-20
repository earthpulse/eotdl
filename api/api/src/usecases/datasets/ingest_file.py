from datetime import datetime
import zipfile
import io
import os
import geopandas as gpd
import json
import shutil
import pystac

from .retrieve_dataset import retrieve_owned_dataset
from ...errors import DatasetVersionDoesNotExistError
from ...repos import DatasetsDBRepo, GeoDBRepo, MongoDBRepo
from ..files import ingest_file, ingest_existing_file
from ..user import retrieve_user_credentials
from .stac import MLDatasetQualityMetrics
from ..utils.stac import STACDataFrame


async def ingest_dataset_file(file, dataset_id, checksum, user, version):
    dataset = retrieve_owned_dataset(dataset_id, user.uid)
    versions = [v.version_id for v in dataset.versions]
    if not version in versions:
        raise DatasetVersionDoesNotExistError()
    file_size = await ingest_file(
        file.filename,
        file.file,
        version,
        dataset_id,
        checksum,
        dataset.files,
    )
    version = [v for v in dataset.versions if v.version_id == version][0]
    version.size += file_size
    dataset.updatedAt = datetime.now()
    dataset_db_repo = DatasetsDBRepo()
    dataset_db_repo.update_dataset(dataset.id, dataset.dict())
    return dataset.id, dataset.name, file.filename


async def ingest_dataset_files_batch(batch, dataset_id, checksums, user, version):
    dataset = retrieve_owned_dataset(dataset_id, user.uid)
    versions = [v.version_id for v in dataset.versions]
    if not version in versions:
        raise DatasetVersionDoesNotExistError()
    # Decompress the received zip file
    tmp_path = f"/tmp/{user.uid}/{dataset_id}/{version}"
    os.makedirs(tmp_path, exist_ok=True)
    batch_size = 0
    with zipfile.ZipFile(io.BytesIO(await batch.read()), "r") as zf:
        zf.extractall(tmp_path)
    # ingest files
    for file, checksum in zip(zf.namelist(), checksums):
        path = os.path.join(tmp_path, file)
        file_size = await ingest_file(
            file,
            path,
            version,
            dataset_id,
            checksum,
            dataset.files,
        )
        batch_size += file_size
    version = [v for v in dataset.versions if v.version_id == version][0]
    version.size += batch_size
    dataset.updatedAt = datetime.now()
    dataset_db_repo = DatasetsDBRepo()
    dataset_db_repo.update_dataset(dataset.id, dataset.dict())
    return dataset.id, dataset.name, zf.namelist()


def add_files_batch_to_dataset_version(filenames, checksums, dataset_id, version, user):
    dataset = retrieve_owned_dataset(dataset_id, user.uid)
    versions = [v.version_id for v in dataset.versions]
    if not version in versions:
        raise DatasetVersionDoesNotExistError()
    batch_size = 0
    for filename, checksum in zip(filenames, checksums):
        file_size = ingest_existing_file(
            filename,
            checksum,
            version,
            dataset.files,
            dataset_id,
            dataset.quality,
        )
        batch_size += file_size
    version = [v for v in dataset.versions if v.version_id == version][0]
    version.size += batch_size  # for Q0+ will add, so put to 0 before if necessary
    dataset.updatedAt = datetime.now()
    dataset_db_repo = DatasetsDBRepo()
    dataset_db_repo.update_dataset(dataset.id, dataset.dict())
    return dataset.id, dataset.name, filenames


def ingest_stac(stac, dataset_id, user):
    # check if dataset exists
    dataset = retrieve_owned_dataset(dataset_id, user.uid)
    # TODO: check all assets exist in os
    # generate catalog
    values = gpd.GeoDataFrame.from_features(stac["features"], crs="4326")  # ???
    # values.to_csv("/tmp/iepa.csv")
    catalog = values[values["type"] == "Catalog"]
    items = values.drop_duplicates(subset="geometry")
    items = items[items["type"] == "Feature"]
    # convert to geojson
    items = json.loads(items.to_json())
    assert len(catalog) == 1, "STAC catalog must have exactly one root catalog"
    catalog = json.loads(catalog.to_json())["features"][0]["properties"]
    keys = list(catalog.keys())
    dataset_quality = 1
    # TODO: validate Q1 dataset with required fields/extensions (author, license)
    # TODO: validate Q2 dataset, not only check name
    if "ml-dataset:name" in keys:
        dataset_quality = 2
        # compute and report automatic qa metrics
        # save stac locally
        tmp_path = f"/tmp/{dataset_id}"
        df = STACDataFrame(values)
        df.to_stac(tmp_path)
        # compute metrics
        catalog_path = f"{tmp_path}/{dataset.name}/catalog.json"
        MLDatasetQualityMetrics.calculate(catalog_path)
        # overwrite catalog with computed metrics
        df = STACDataFrame.from_stac_file(catalog_path)
        catalog = df[df["type"] == "Catalog"]
        # print("1", catalog)
        catalog = json.loads(catalog.to_json())["features"][0]["properties"]
        # print("2", catalog)
        # delete tmp files
        shutil.rmtree(tmp_path)
    print("quality", dataset_quality)
    # ingest to geodb
    # credentials = retrieve_user_credentials(user)
    # geodb_repo = GeoDBRepo(credentials)
    # geodb_repo.insert(dataset.id, values)
    geodb_repo = MongoDBRepo()
    geodb_repo.insert(dataset.id, values)
    # the catalog should contain all the info we want to show in the UI
    dataset.catalog = catalog
    # dataset.items = items
    dataset.quality = dataset_quality
    repo = DatasetsDBRepo()
    dataset.updatedAt = datetime.now()
    repo.update_dataset(dataset.id, dataset.model_dump())
    return dataset
