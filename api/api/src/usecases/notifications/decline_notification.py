from datetime import datetime

from ...models import NotificationStatus, NotificationType, Notification, ChangeStatus
from ...repos import NotificationsDBRepo, ChangesDBRepo
from .retrieve_notifications import retrieve_owned_notification
from ..changes import retrieve_change

def decline_notification(id, user):
    repo = NotificationsDBRepo()
    notification = retrieve_owned_notification(id, user)
    # side effects
    if notification.type == NotificationType.DATASET_UPDATE:
        changes_repo = ChangesDBRepo()
        change = retrieve_change(notification.payload["change_id"])
        change.status = ChangeStatus.REJECTED
        change.updatedAt = datetime.now()
        changes_repo.update_change(change.id, change.model_dump())
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
    # update notification
    notification.status = NotificationStatus.DECLINED
    notification.updatedAt = datetime.now()
    repo.update_notification(notification.id, notification.model_dump())
    return notification
