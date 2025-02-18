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
        repo = NotificationsDBRepo()
        new_notification_id = repo.generate_id()
        new_notification = Notification(
            uid=change.uid,
            id=new_notification_id,
            type=NotificationType.DATASET_UPDATE_REQUEST_DECLINED,
            payload={
                "message": f"Your dataset update request for {change.payload['name']} has been declined.",
            },
        )
        repo.persist_notification(new_notification.model_dump(), new_notification_id)
    return change