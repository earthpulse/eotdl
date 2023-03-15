from .client import get_db
from bson.objectid import ObjectId
from datetime import datetime, timedelta, time

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

    def retrieve(self, collection, value=None, field='id'):
        if value is None:
            return list(self.db[collection].find())
        if field == '_id':
            value = ObjectId(value)
        return self.db[collection].find_one({field: value})

    def update(self, collection, id, data):
        return self.db[collection].update_one({'_id': ObjectId(id)}, {'$set': data})

    def delete(self, collection, id):
        return self.db[collection].delete_one({'_id': ObjectId(id)})

    def retrieve_all(self, collection):
        return list(self.db[collection].find())
    
    def find_one_by_field(self, collection, field, value):
        return self.db[collection].find_one({field: value})
    
    def find_one_by_name(self, collection, name):
        return self.find_one_by_field(collection, 'name', name)
    
    def increase_counter(self, collection, field, value=1):
        return self.db[collection].update_one({}, {'$inc': {field: value}})
    
    def find_in_time_range(self, collection, uid, value, field="type", t0=datetime.combine(datetime.today(), time.min), dt=timedelta(days=1)):
        return list(self.db[collection].find({
            'uid': uid,
            field: value,
            'timestamp': {'$gte': t0, '$lt': t0 + dt}
        }))