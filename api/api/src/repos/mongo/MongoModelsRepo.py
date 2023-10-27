from datetime import datetime

from .MongoRepo import MongoRepo


class MongoModelsRepo(MongoRepo):
    def __init__(self):
        super().__init__()

    def retrieve_models(self, name, limit):
        match = {}
        if name is not None:
            match = {"name": {"$regex": name, "$options": "i"}}
        return self.retrieve("models", limit=limit, match=match)

    def retrieve_model(self, model_id):
        return self.retrieve("models", model_id)

    def find_one_model_by_name(self, name):
        return self.find_one_by_name("models", name)

    def persist_files(self, files, id):
        return self.persist("files", files, id)

    def persist_model(self, model, id):
        return self.persist("models", model, id)

    def increase_user_model_count(self, uid):
        return self.increase_counter("users", "uid", uid, "models_count")

    def create_model_version(self, model, version):
        return self._update(
            "models",
            {"id": model.id},
            {
                "$set": {"updated_at": datetime.now()},
                "$push": {"versions": version},
            },
        )

    def retrieve_models_leaderboard(self):
        return self.find_top("users", "models_count", 5)

    def update_model(self, model_id, model):
        return self.update("models", model_id, model)
