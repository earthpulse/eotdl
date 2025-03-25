from ...models import Notification
from ...repos import NotificationsDBRepo

def create_notification(uid, type, payload):
    notifications_repo = NotificationsDBRepo()
    notification_id = notifications_repo.generate_id()
    notification = Notification(
        id=notification_id,
        uid=uid,
        type=type,
        payload=payload,
    )
    notifications_repo.persist_notification(notification.model_dump(), notification_id)
    return notification