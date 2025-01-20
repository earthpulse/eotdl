from datetime import datetime

from ...repos import DatasetsDBRepo
from .retrieve_dataset import (
    retrieve_dataset,
    retrieve_owned_dataset,
    retrieve_dataset_by_name,
)
from ..user import retrieve_user
from ...errors import (
    DatasetAlreadyExistsError,
    DatasetDoesNotExistError,
    InvalidTagError,
)
from ...models import Dataset


def toggle_like_dataset(dataset_id, user):
    repo = DatasetsDBRepo()
    dataset = retrieve_dataset(dataset_id)
    user = retrieve_user(user.uid)
    if dataset.id in user.liked_datasets:
        repo.unlike_dataset(dataset_id, user.uid)
    else:
        repo.like_dataset(dataset_id, user.uid)
    return "done"


def update_dataset(
    dataset_id, user, name, authors, source, license, tags, description, thumbnail
):
    dataset = retrieve_owned_dataset(dataset_id, user.uid)
    # validate name
    if name:
        try:
            _dataset = retrieve_dataset_by_name(name)
            if _dataset.id != dataset_id:
                raise DatasetAlreadyExistsError()
        except DatasetDoesNotExistError:
            pass
    # validate tags
    repo = DatasetsDBRepo()
    if tags:
        tags_data = repo.retrieve_tags()
        all_tags = [tag["name"] for tag in tags_data]
        for tag in tags:
            if tag not in all_tags:
                raise InvalidTagError()
    # update dataset
    data = dataset.model_dump()
    data.update(
        updatedAt=datetime.now(),
        description=description if description is not None else dataset.description,
        tags=tags if tags is not None else dataset.tags,
    )
    if data["quality"] == 0:
        data.update(
            name=name if name is not None else dataset.name,
            authors=authors if authors is not None else dataset.authors,
            source=source if source is not None else dataset.source,
            license=license if license is not None else dataset.license,
            thumbnail=thumbnail if thumbnail is not None else dataset.thumbnail,
        )
    updated_dataset = Dataset(**data)
    # update dataset in db
    repo.update_dataset(dataset_id, updated_dataset.model_dump())
    return updated_dataset
