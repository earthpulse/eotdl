from .MongoRepo import MongoRepo

class MongoUserRepo(MongoRepo):
    def __init__(self):
        super().__init__()

    def retrieve_user_by_uid(self, uid):
        return self.retrieve("users", uid, "uid")
    
    def update_user(self, id, data):
        return self.update("users", id, data)
    
    def persist_user(self, data, id):
        return self.persist("users", data, id)
    
    def find_one_user_by_name(self, name):
        return self.find_one_by_name('users', name)
    
    def check_user_exists(self, uid):
        return self.exists("users", uid, "uid")
    
    def retrieve_tier(self, tier):
        return self.find_one_by_name("tiers", tier)
    
    def retrieve_usage(self, uid):
        return self.find_in_time_range("usage", uid, "dataset_ingested", "type")
