from datetime import datetime

from .MongoRepo import MongoRepo


class MongoModelsRepo(MongoRepo):
    def __init__(self):
        super().__init__()

    def retrieve_models(self, name, limit):
        match = {}
        if name is not None:
            match = {"name": {"$regex": name, "$options": "i"}}
        # uncomment if we implement private models
        # if limit is not None:
        #     match['active'] = True
        #     match['visibility'] = 'public'
        return self.retrieve(
            "models", limit=limit, match=match, sort="createdAt", order=-1
        )

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

    def decrease_user_model_count(self, uid):
        return self.increase_counter("users", "uid", uid, "models_count", -1)

    def create_model_version(self, model, version):
        return self._update(
            "models",
            {"id": model.id},
            {
                "$set": {"updated_at": datetime.now()},
                "$push": {"versions": version},
            },
        )
    
    def deactivate_model(self, model_id):
        return self._update(
            "models",
            {"id": model_id},
            {
                "$set": {
                    "active": False,
                }
            },
        )

    def retrieve_models_leaderboard(self):
        return self.find_top("users", "models_count", 5)

    def update_model(self, model_id, model):
        return self.update("models", model_id, model)

    def retrieve_popular_models(self, limit):
        match = {}  
        # uncomment if we implement private models
        # if limit is not None:
        #     match ={'active': True, 'visibility': 'public'}
        return self.find_top("models", "likes", limit, match=match)

    def like_model(self, model_id, uid):
        self.increase_counter("models", "_id", model_id, "likes", 1)
        return self.append_to_list("users", "uid", uid, "liked_models", model_id)

    def unlike_model(self, model_id, uid):
        self.increase_counter("models", "_id", model_id, "likes", -1)
        return self.remove_from_list("users", "uid", uid, "liked_models", model_id)

    def delete_model(self, model_id):
        return self.delete("models", model_id)

    def delete_files(self, files_id):
        return self.delete("files", files_id)

    def retrieve_tags(self):
        return self.retrieve("tags")

    def allow_user_to_model(self, model_id, uid):
        return self.append_to_list("models", "id", model_id, "allowed_users", uid)
    