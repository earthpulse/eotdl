from shapely.geometry import Polygon
from .client import get_client


class GeoDBRepo:
    def __init__(self, credentials):
        self.client = get_client(credentials)
        self.database = None

    def exists(self, collection):
        return self.client.collection_exists(collection, database=self.database)

    def delete(self, collection):
        return self.client.drop_collection(collection, database=self.database)

    def create(self, collections):
        return self.client.create_collections(collections, database=self.database)

    def insert(self, collection, values):
        values.rename(columns={"id": "stac_id"}, inplace=True)
        # convert None geometry to empty geometry wkt
        values.geometry = values.geometry.apply(lambda x: Polygon() if x is None else x)
        if self.exists(collection):  # DELETEING COLLECTION IF EXISTS !!!
            self.delete(collection)
        collections = {collection: self.create_collection_structure(values.columns)}
        self.create(collections)
        self.client.insert_into_collection(
            collection, database=self.database, values=values
        )
        self.client.publish_collection(collection, self.database)

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
