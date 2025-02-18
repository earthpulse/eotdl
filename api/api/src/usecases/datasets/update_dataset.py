from datetime import datetime

from ...repos import DatasetsDBRepo, ChangesDBRepo, NotificationsDBRepo
from .retrieve_dataset import (
    retrieve_dataset,
    retrieve_dataset_by_name,
    # retrieve_owned_dataset,
)
# from ..user import retrieve_user
from ...errors import (
    DatasetAlreadyExistsError,
    DatasetDoesNotExistError,
#     InvalidTagError,
)
from ...models import Dataset, Change, Notification, ChangeType, NotificationType


# def toggle_like_dataset(dataset_id, user):
#     repo = DatasetsDBRepo()
#     dataset = retrieve_dataset(dataset_id)
#     user = retrieve_user(user.uid)
#     if dataset.id in user.liked_datasets:
#         repo.unlike_dataset(dataset_id, user.uid)
#     else:
#         repo.like_dataset(dataset_id, user.uid)
#     return "done"


def update_dataset(
    dataset_id, user, dataset
):
    _dataset = retrieve_dataset(dataset_id)
    if user.uid != _dataset.uid:
        # user is not the owner of the dataset, so any change should be approved by the owner or moderators
        return propose_dataset_update(dataset_id, user, dataset)
    
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

    # update dataset
    repo = DatasetsDBRepo()
    data = dataset.model_dump()
    data.update(updatedAt=datetime.now())
    updated_dataset = Dataset(**data)
    # update dataset in db
    repo.update_dataset(dataset_id, updated_dataset.model_dump())
    return updated_dataset

def propose_dataset_update(dataset_id, user, dataset):
    changes_repo = ChangesDBRepo()
    change_id = changes_repo.generate_id()
    change = Change(
        id=change_id,
        uid=user.uid,
        type=ChangeType.DATASET_UPDATE,
        payload=dataset,
    )
    changes_repo.persist_change(change.model_dump(), change_id)
    notifications_repo = NotificationsDBRepo()
    notification_id = notifications_repo.generate_id()
    notification = Notification(
        id=notification_id,
        uid=dataset.uid,
        type=NotificationType.DATASET_UPDATE,
        payload={
            'change_id': change_id,
        },
    )
    notifications_repo.persist_notification(notification.model_dump(), notification_id)
    return dataset