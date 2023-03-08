import pymongo
from pymongo import MongoClient
import os

client = MongoClient(os.environ['MONGO_URL'])

def get_db(name=None):
	return client[os.environ['MONGO_DB_NAME']]
