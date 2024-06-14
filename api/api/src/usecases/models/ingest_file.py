from datetime import datetime
import zipfile
import io
import os
import geopandas as gpd
import json

from .retrieve_model import retrieve_owned_model
from ...errors import ModelVersionDoesNotExistError
from ...repos import ModelsDBRepo, GeoDBRepo
from ..files import ingest_file, ingest_existing_file
from ..utils.stac import STACDataFrame
from ..user import retrieve_user_credentials


async def ingest_model_file(file, model_id, checksum, user, version):
    model = retrieve_owned_model(model_id, user.uid)
    versions = [v.version_id for v in model.versions]
    if not version in versions:
        raise ModelVersionDoesNotExistError()
    file_size = await ingest_file(
        file.filename,
        file.file,
        version,
        model_id,
        checksum,
        model.files,
    )
    version = [v for v in model.versions if v.version_id == version][0]
    version.size += file_size
    model.updatedAt = datetime.now()
    model_db_repo = ModelsDBRepo()
    model_db_repo.update_model(model.id, model.dict())
    return model.id, model.name, file.filename


async def ingest_model_files_batch(batch, model_id, checksums, user, version):
    model = retrieve_owned_model(model_id, user.uid)
    versions = [v.version_id for v in model.versions]
    if not version in versions:
        raise ModelVersionDoesNotExistError()
    # Decompress the received zip file
    tmp_path = f"/tmp/{user.uid}/{model_id}/{version}"
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
            model_id,
            checksum,
            model.files,
        )
        batch_size += file_size
    version = [v for v in model.versions if v.version_id == version][0]
    version.size += batch_size  # for Q0+ will add, so put to 0 before if necessary
    model.updatedAt = datetime.now()
    model_db_repo = ModelsDBRepo()
    model_db_repo.update_model(model.id, model.dict())
    return model.id, model.name, zf.namelist()


def add_files_batch_to_model_version(filenames, checksums, model_id, version, user):
    model = retrieve_owned_model(model_id, user.uid)
    versions = [v.version_id for v in model.versions]
    if not version in versions:
        raise ModelVersionDoesNotExistError()
    batch_size = 0
    for filename, checksum in zip(filenames, checksums):
        file_size = ingest_existing_file(
            filename,
            checksum,
            version,
            model.files,
            model_id,
            model.quality,
        )
        batch_size += file_size
    version = [v for v in model.versions if v.version_id == version][0]
    version.size += batch_size  # for Q0+ will add, so put to 0 before if necessary
    model.updatedAt = datetime.now()
    model_db_repo = ModelsDBRepo()
    model_db_repo.update_model(model.id, model.dict())
    return model.id, model.name, filenames


def ingest_stac(stac, model_id, user):
    # check if model exists
    model = retrieve_owned_model(model_id, user.uid)
    # TODO: check all assets exist in os
    # generate catalog
    values = gpd.GeoDataFrame.from_features(stac["features"], crs="4326")  # ???
    # values.to_csv("/tmp/iepa.csv")
    print(values)
    catalog = values[values["type"] == "Catalog"]
    items = values.drop_duplicates(subset="geometry")
    items = items[items["type"] == "Feature"]
    assert len(catalog) == 1, "STAC catalog must have exactly one root catalog"
    assert len(items) == 1, "Only one item is allowed"
    catalog = json.loads(catalog.to_json())["features"][0]["properties"]
    item = json.loads(items.to_json())["features"][0]["properties"]
    print(item)
    model_quality = 1
    # TODO: validate Q2 model, not only check name
    if "mlm:name" in item["properties"]:
        model_quality = 2
        # compute metrics like we do for Q2 models ?
    print("quality", model_quality)
    # ingest to geodb
    credentials = retrieve_user_credentials(user)
    geodb_repo = GeoDBRepo(credentials)
    geodb_repo.insert(model.id, values)
    # the catalog should contain all the info we want to show in the UI
    model.catalog = catalog  # OJO ! this is not the same as the model catalog
    model.items = item
    model.quality = model_quality
    repo = ModelsDBRepo()
    model.updatedAt = datetime.now()
    repo.update_model(model.id, model.model_dump())
    return model
