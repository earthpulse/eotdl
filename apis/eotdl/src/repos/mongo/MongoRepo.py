from .client import get_db
from bson.objectid import ObjectId


class MongoRepo():

    def __init__(self):
        self.db = get_db()

    def exists(self, collection, id):
        return self.db[collection].find_one({'_id': ObjectId(id)}) is not None

    def generate_id(self):
        return str(ObjectId())

    def persist(self, collection, data, id=None):
        if id is not None: 
            data['_id'] = ObjectId(id)
            return self.db[collection].insert_one(data)
        return self.db[collection].insert_one(data).inserted_id

    def retrieve(self, collection, value, field='id'):
        if field == '_id':
            value = ObjectId(value)
        return self.db[collection].find_one({field: value})

    def update(self, collection, id, data):
        return self.db[collection].update_one({'_id': ObjectId(id)}, {'$set': data})

    def delete(self, collection, id):
        return self.db[collection].delete_one({'_id': ObjectId(id)})

    def retrieve_all(self, collection):
        return list(self.db[collection].find())