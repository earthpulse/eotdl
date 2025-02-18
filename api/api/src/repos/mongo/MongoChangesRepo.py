from .MongoRepo import MongoRepo

class MongoChangesRepo(MongoRepo):
    def __init__(self):
        super().__init__()

    def retrieve_change(self, change_id):
        return self.retrieve("changes", change_id)

    def persist_change(self, change, id):
        return self.persist("changes", change, id)

    def update_change(self, change_id, change):
        return self.update("changes", change_id, change)

    def delete_change(self, change_id):
        return self.delete("changes", change_id)
