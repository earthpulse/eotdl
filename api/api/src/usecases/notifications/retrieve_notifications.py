from ...repos import NotificationsDBRepo
from ...models import Notification

def retrieve_notifications(user):
    repo = NotificationsDBRepo()
    data = repo.retrieve_notifications(user.uid)
    notifications = [Notification(**item) for item in data if item["status"] == "unread"]
    return notifications

def retrieve_owned_notification(id, user):
    repo = NotificationsDBRepo()
    data = repo.retrieve_notifications(user.uid)
    notification = [item for item in data if item["id"] == id]
    if len(notification) != 1:
        raise ValueError("Notification not found")
    return Notification(**notification[0])
