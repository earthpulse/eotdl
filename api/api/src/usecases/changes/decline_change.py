from datetime import datetime

from ...repos import NotificationsDBRepo, ChangesDBRepo
from ...models import NotificationType, Notification, ChangeStatus, ChangeType
from .retrieve_change import retrieve_change

def decline_change(change_id, user):
    changes_repo = ChangesDBRepo()
    change = retrieve_change(change_id)
    if change.status != ChangeStatus.PENDING:
        raise Exception("Change is not pending")
    change.status = ChangeStatus.REJECTED
    change.updatedAt = datetime.now()
    changes_repo.update_change(change.id, change.model_dump())
    if change.type == ChangeType.DATASET_UPDATE:
        type = NotificationType.DATASET_UPDATE_REQUEST_DECLINED
        message = f"Your dataset update request for {change.payload['name']} has been declined."
    elif change.type == ChangeType.MODEL_UPDATE:
        type = NotificationType.MODEL_UPDATE_REQUEST_DECLINED
        message = f"Your model update request for {change.payload['name']} has been declined."
    elif change.type == ChangeType.PIPELINE_UPDATE:
        type = NotificationType.PIPELINE_UPDATE_REQUEST_DECLINED
        message = f"Your pipeline update request for {change.payload['name']} has been declined."
    else:
        raise Exception("Invalid change type")
    repo = NotificationsDBRepo()
    new_notification_id = repo.generate_id()
    new_notification = Notification(
        uid=change.uid,
        id=new_notification_id,
        type=type,
        payload={
            "message": message,
        },
    )
    repo.persist_notification(new_notification.model_dump(), new_notification_id)
    return change