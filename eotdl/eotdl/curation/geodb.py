import os 
from xcube_geodb.core.geodb import GeoDBClient

def ingest(
	collection: str,
	server_url: str = os.environ["SERVER_URL"],
	server_port: int = os.environ["SERVER_PORT"],
	client_id: str = os.environ["CLIENT_ID"],
	client_secret: str = os.environ["CLIENT_SECRET"],
	auth_aud: str = os.environ["AUTH_DOMAIN"],
	database: str = None,
):
	"""
	Create a GeoDB collection from a STACDataFrame

	:param collection: dataset name (GeoDB collection)
	:param server_url: GeoDB server url
	:param server_port: GeoDB server port
	:param client_id: GeoDB client id
	:param client_secret: GeoDB client secret
	:param auth_aud: GeoDB auth aud
	:param database: GeoDB database
	"""

	geodb_client = GeoDBClient(
		server_url=server_url,
		server_port=server_port,
		client_id=client_id,
		client_secret=client_secret,
		auth_aud=auth_aud,
	)

	# TODO: check name is unique 

	# TODO: ingest assets (only if local)
	# TODO: rename assets in the dataframe with URLs (only if local)

	# ingest to geodb

	# Check if the collection already exists
	if geodb_client.collection_exists(collection, database=database):
		# geodb_client.drop_collection(collection, database=database)
		raise Exception(f"Collection {collection} already exists")

	# Rename the column id to stac_id, to avoid conflicts with the id column
	self.rename(columns={"id": "stac_id"}, inplace=True)
	# Fill the NaN with '' to avoid errors, except in the geometry column
	copy = self.copy()
	columns_to_fill = copy.columns.drop("geometry")
	self[columns_to_fill] = self[columns_to_fill].fillna("")

	# Create the collection if it does not exist
	# and insert the data
	collections = {collection: self._create_collection_structure(self.columns)}
	geodb_client.create_collections(collections, database=database)

	geodb_client.insert_into_collection(collection, database=database, values=self)

	# TODO: save data in eotdl