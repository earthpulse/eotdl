from datetime import datetime

from .retrieve_dataset import retrieve_owned_dataset
from ...errors import DatasetVersionDoesNotExistError
from ...repos import DatasetsDBRepo
from ..files import ingest_file, ingest_existing_file


async def ingest_dataset_file(file, dataset_id, version, parent, checksum, user):
    dataset = retrieve_owned_dataset(dataset_id, user.uid)
    versions = [v.version_id for v in dataset.versions]
    if not version in versions:
        raise DatasetVersionDoesNotExistError()
    filename, file_size = await ingest_file(
        file, version, parent, dataset_id, checksum, dataset.quality, dataset.files
    )
    version = [v for v in dataset.versions if v.version_id == version][0]
    version.size += file_size  # for Q0+ will add, so put to 0 before if necessary
    dataset.updatedAt = datetime.now()
    dataset_db_repo = DatasetsDBRepo()
    dataset_db_repo.update_dataset(dataset.id, dataset.dict())
    return dataset.id, dataset.name, filename


async def ingest_existing_dataset_file(
    filename, dataset_id, file_version, version, checksum, user
):
    dataset = retrieve_owned_dataset(dataset_id, user.uid)
    versions = [v.version_id for v in dataset.versions]
    if not version in versions:
        raise DatasetVersionDoesNotExistError()
    filename, file_size = await ingest_existing_file(
        filename,
        version,
        dataset.files,
        file_version,
        dataset_id,
        checksum,
        dataset.quality,
    )
    version = [v for v in dataset.versions if v.version_id == version][0]
    version.size += file_size  # for Q0+ will add, so put to 0 before if necessary
    dataset.updatedAt = datetime.now()
    dataset_db_repo = DatasetsDBRepo()
    dataset_db_repo.update_dataset(dataset.id, dataset.dict())
    return dataset.id, dataset.name, filename


def ingest_file_url():
    # TODO
    return
    # def get_file_name(self, file):
    #     return file.split("/")[-1]

    # def persist_file(self, file, dataset_id, filename):
    #     return os_repo.persist_file_url(file, dataset_id, filename)


def ingest_stac():
    # TODO
    return
    # # check if dataset exists
    # data = db_repo.retrieve("datasets", dataset)
    # if not data:
    #     raise DatasetDoesNotExistError()
    # dataset = STACDataset(**data)
    # # check user owns dataset
    # if dataset.uid != user.uid:
    #     raise DatasetDoesNotExistError()
    # # TODO: check all assets exist in os
    # # ingest to geodb
    # credentials = retrieve_user_credentials(user)
    # geodb_repo = geodb_repo(credentials)
    # catalog = geodb_repo.insert(dataset, stac)
    # # the catalog should contain all the info we want to show in the UI
    # dataset.catalog = catalog
    # keys = list(catalog.keys())
    # if "ml-dataset:name" in keys:
    #     dataset.quality = 2
    #     # TODO: compute and report automatic qa metrics
    # # TODO: validate Q2 dataset, not only check name
    # # TODO: validate Q1 dataset with required fields/extensions (author, license)
    # db_repo.update("datasets", dataset, dataset.model_dump())
    # return Outputs(dataset=dataset)
