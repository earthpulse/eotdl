from .MongoRepo import MongoRepo


class MongoAuthRepo(MongoRepo):
    def __init__(self):
        super().__init__()
        self.collection = "auth_states"

    def create_auth_state(self, data):
        return self.persist(self.collection, data)

    def update_auth_state(self, state, code):
        return self._update(self.collection, {"state": state}, {"$set": {"code": code}})

    def retrieve_auth_state(self, state):
        return self.find_one(self.collection, {"state": state})

    def delete_auth_state(self, state):
        return self.delete(self.collection, state, "state")
