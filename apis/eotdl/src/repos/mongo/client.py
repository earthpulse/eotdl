from pymongo import MongoClient
import os

client = MongoClient(os.environ['MONGO_URL'])

def get_db():
	return client[os.environ['MONGO_DB_NAME']]