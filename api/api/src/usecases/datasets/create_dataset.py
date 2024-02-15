from ...models import Dataset, Files, STACDataset
from ...errors import (
    DatasetAlreadyExistsError,
    DatasetDoesNotExistError,
)
from ...repos import DatasetsDBRepo, GeoDBRepo

from .retrieve_dataset import retrieve_dataset_by_name
from ..user import check_user_can_create_dataset, retrieve_user_credentials


def create_dataset(user, name, authors, source, license, thumbnail):
    repo = DatasetsDBRepo()
    try:
        retrieve_dataset_by_name(name)
        raise DatasetAlreadyExistsError()
    except DatasetDoesNotExistError:
        check_user_can_create_dataset(user)
        id, files_id = repo.generate_id(), repo.generate_id()
        files = Files(id=files_id, dataset=id)
        dataset = Dataset(
            uid=user.uid,
            id=id,
            files=files_id,
            name=name,
            authors=authors,
            source=source,
            license=license,
            thumbnail=thumbnail,
        )
        repo.persist_files(files.model_dump(), files.id)
        repo.persist_dataset(dataset.model_dump(), dataset.id)
        repo.increase_user_dataset_count(user.uid)
        return dataset.id


def create_stac_dataset(user, name):
    repo = DatasetsDBRepo()
    credentials = retrieve_user_credentials(user)
    geodb_repo = GeoDBRepo(credentials)  # validate credentials
    try:
        retrieve_dataset_by_name(name)
        raise DatasetAlreadyExistsError()
    except DatasetDoesNotExistError:
        check_user_can_create_dataset(user)
        id, files_id = repo.generate_id(), repo.generate_id()
        files = Files(id=files_id, dataset=id)
        dataset = STACDataset(
            uid=user.uid,
            id=id,
            name=name,
            files=files_id,
        )
        repo.persist_files(files.model_dump(), files.id)
        repo.persist_dataset(dataset.model_dump(), dataset.id)
        repo.increase_user_dataset_count(user.uid)
        return dataset.id
