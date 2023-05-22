from pymongo import MongoClient
import os

client = MongoClient(os.environ['MONGO_URL'])

def get_db(name=os.environ['MONGO_DB_NAME']):
	return client[name]