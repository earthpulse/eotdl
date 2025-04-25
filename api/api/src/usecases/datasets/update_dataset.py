from datetime import datetime

from ...repos import DatasetsDBRepo
from .retrieve_dataset import (
    retrieve_dataset,
    retrieve_dataset_by_name,
)
from ..user import retrieve_user
from ...errors import (
    DatasetAlreadyExistsError,
    DatasetDoesNotExistError,
)
from ...models import Dataset, ChangeType, NotificationType
from ..notifications import create_notification
from ..changes import create_change

def update_dataset(
    dataset_id, user, dataset
):
    _dataset = retrieve_dataset(dataset_id)
    if user.uid != _dataset.uid:
        # user is not the owner of the dataset, so any change should be approved by the owner or moderators
        return propose_dataset_update(_dataset.name, user, dataset)
    
    # update name
    if dataset.name != _dataset.name:
        try:
            __dataset = retrieve_dataset_by_name(dataset.name)
            if __dataset.id != dataset_id:
                raise DatasetAlreadyExistsError()
        except DatasetDoesNotExistError:
            pass

    # # validate tags
    # if tags:
    #     tags_data = repo.retrieve_tags()
    #     all_tags = [tag["name"] for tag in tags_data]
    #     for tag in tags:
    #         if tag not in all_tags:
    #             raise InvalidTagError()

    # update dataset (only name and metadata)
    _dataset.name = dataset.name
    _dataset.metadata = dataset.metadata
    _dataset.updatedAt = datetime.now()
    
    # make private
    if not _dataset.allowed_users and dataset.private:
        _dataset.allowed_users = [dataset.uid]

    # make public
    if _dataset.allowed_users and not dataset.private:
        _dataset.allowed_users = []
    
    # update dataset in db
    repo = DatasetsDBRepo()
    repo.update_dataset(dataset_id, _dataset.model_dump())
    return _dataset

def propose_dataset_update(dataset_name, user, dataset):
    change = create_change(
        user,
        ChangeType.DATASET_UPDATE,
        dataset,
    )
    create_notification(
        dataset.uid, 
        NotificationType.DATASET_UPDATE, 
        {
            'change_id': change.id,
            'dataset_name': dataset_name,
        }
    )
    return dataset


def toggle_like_dataset(dataset_id, user):
    repo = DatasetsDBRepo()
    dataset = retrieve_dataset(dataset_id)
    user = retrieve_user(user.uid)
    if dataset.id in user.liked_datasets:
        repo.unlike_dataset(dataset_id, user.uid)
    else:
        repo.like_dataset(dataset_id, user.uid)
    return "done"