from ...models import Dataset, Metadata
from ...errors import (
    DatasetAlreadyExistsError,
    DatasetDoesNotExistError,
)
from ...repos import DatasetsDBRepo

from .retrieve_dataset import retrieve_dataset_by_name
from ..user import check_user_can_create_dataset


def create_dataset(user, name, authors, source, license, thumbnail, description):
    repo = DatasetsDBRepo()
    try:
        retrieve_dataset_by_name(name)
        raise DatasetAlreadyExistsError()
    except DatasetDoesNotExistError:
        check_user_can_create_dataset(user)
        id = repo.generate_id()
        dataset = Dataset(
            uid=user.uid,
            id=id,
            name=name,
            metadata=Metadata(
                authors=authors,
                source=source,
                license=license,
                thumbnail=thumbnail,
                description=description,
            ),
            active=True
        )
        repo.persist_dataset(dataset.model_dump(), dataset.id)
        repo.increase_user_dataset_count(user.uid)
        return dataset