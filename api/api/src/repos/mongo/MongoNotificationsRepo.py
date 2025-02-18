from .MongoRepo import MongoRepo

class MongoNotificationsRepo(MongoRepo):
    def __init__(self):
        super().__init__()

    def retrieve_notifications(self, uid):
        return self.retrieve("notifications", match={"uid": uid}, sort="createdAt", order=-1)

    def persist_notification(self, notification, id):
        return self.persist("notifications", notification, id)

    def update_notification(self, notification_id, notification):
        return self.update("notifications", notification_id, notification)

    def delete_notification(self, notification_id):
        return self.delete("notifications", notification_id)
