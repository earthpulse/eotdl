from shapely.geometry import Polygon
# from .client import get_client
from pymongo import MongoClient
import os

# mock geodb with mongo

client = MongoClient(os.environ['MONGO_URL'])

class MongoDBRepo:
    def __init__(self):
        self.database = client['geodb-mock']
        # if not self.client.database_exists(self.database):
        #     self.client.create_database(self.database)

    def exists(self, collection):
        # return self.client.collection_exists(collection, database=self.database)
        return self.database[collection].count_documents({}) > 0

    def delete(self, collection):
        # return self.client.drop_collection(collection, database=self.database)
        return self.database[collection].delete_many({})

    def create(self, collections):
        # return self.client.create_collections(collections, database=self.database)
        pass
		

    def insert(self, collection, values):
        values.rename(columns={"id": "stac_id"}, inplace=True)

        # remove geometry column for now
        values.drop(columns=["geometry"], inplace=True)


        if self.exists(collection):  # DELETEING COLLECTION IF EXISTS !!!
            self.delete(collection)

        # collections = {collection: self.create_collection_structure(values.columns)}
        # self.create(collections)
        # self.client.insert_into_collection(
        #     collection, database=self.database, values=values
        # )
        # self.client.publish_collection(collection, self.database)
        self.database[collection].insert_many(values.to_dict(orient="records"))

    def retrieve(self, collection):
        return self.client.get_collection(collection, database=self.database)

    def create_collection_structure(self, columns: list) -> dict:
        # TODO: in order to query geodb we must set the correct types !!!
        # https://xcube-geodb.readthedocs.io/en/latest/notebooks/geodb_manage_collections.html
        # https://www.postgresql.org/docs/11/datatype.html
        stac_collection = {"crs": 4326, "properties": {}}
        for column in columns:
            if column not in ("geometry", "id"):
                # stac_collection["properties"][column] = "text"
                stac_collection["properties"][column] = "json"
        return stac_collection
