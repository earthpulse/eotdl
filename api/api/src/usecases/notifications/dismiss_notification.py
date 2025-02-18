from datetime import datetime

from ...models import NotificationStatus
from ...repos import NotificationsDBRepo
from .retrieve_notifications import retrieve_owned_notification
from ..changes import decline_change

def dismiss_notification(id, user):
    repo = NotificationsDBRepo()
    notification = retrieve_owned_notification(id, user)
    # side effects (ignore errors)
    try:
        if 'change_id' in notification.payload:
            decline_change(notification.payload["change_id"], user)
    except Exception as e:
        pass
    # update notification
    notification.status = NotificationStatus.DECLINED
    notification.updatedAt = datetime.now()
    repo.update_notification(notification.id, notification.model_dump())
    return notification
