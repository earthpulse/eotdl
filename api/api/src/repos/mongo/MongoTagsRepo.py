from .MongoRepo import MongoRepo

class MongoTagsRepo(MongoRepo):
    def __init__(self):
        super().__init__()

    def retrieve_tags(self):
        return self.retrieve("tags")
