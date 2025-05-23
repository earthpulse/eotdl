from datetime import datetime

from .MongoRepo import MongoRepo


class MongoPipelinesRepo(MongoRepo):
    def __init__(self):
        super().__init__()

    def retrieve_pipelines(self, name, limit):
        match = {}
        if name is not None:
            match = {"name": {"$regex": name, "$options": "i"}}
        return self.retrieve(
            "pipelines", limit=limit, match=match, sort="createdAt", order=-1
        )

    def retrieve_pipeline(self, model_id):
        return self.retrieve("pipelines", model_id)

    def find_one_pipeline_by_name(self, name):
        return self.find_one_by_name("pipelines", name)

    def persist_files(self, files, id):
        return self.persist("files", files, id)

    def persist_pipeline(self, model, id):
        return self.persist("pipelines", model, id)

    def increase_user_pipeline_count(self, uid):
        return self.increase_counter("users", "uid", uid, "models_count")

    def decrease_user_pipeline_count(self, uid):
        return self.increase_counter("users", "uid", uid, "models_count", -1)

    def create_pipeline_version(self, model, version):
        return self._update(
            "pipelines",
            {"id": model.id},
            {
                "$set": {"updated_at": datetime.now()},
                "$push": {"versions": version},
            },
        )
    
    def deactivate_pipeline(self, model_id):
        return self._update(
            "pipelines",
            {"id": model_id},
            {
                "$set": {
                    "active": False,
                }
            },
        )

    def retrieve_pipelines_leaderboard(self):
        return self.find_top("users", "models_count", 5)

    def update_pipeline(self, model_id, model):
        return self.update("pipelines", model_id, model)

    def retrieve_popular_pipelines(self, limit):
        return self.find_top("pipelines", "likes", limit)

    def like_pipeline(self, model_id, uid):
        self.increase_counter("pipelines", "_id", model_id, "likes", 1)
        return self.append_to_list("users", "uid", uid, "liked_pipelines", model_id)

    def unlike_pipeline(self, model_id, uid):
        self.increase_counter("pipelines", "_id", model_id, "likes", -1)
        return self.remove_from_list("users", "uid", uid, "liked_pipelines", model_id)

    def delete_pipeline(self, model_id):
        return self.delete("pipelines", model_id)

    def delete_files(self, files_id):
        return self.delete("files", files_id)

    def retrieve_tags(self):
        return self.retrieve("tags")
