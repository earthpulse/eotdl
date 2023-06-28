from xcube_geodb.core.geodb import GeoDBClient
import os

def get_client():
	return GeoDBClient(
		server_url=os.environ["SERVER_URL"],
		server_port=os.environ["SERVER_PORT"],
		client_id=os.environ["CLIENT_ID"],
		client_secret=os.environ["CLIENT_SECRET"],
		auth_aud=os.environ["AUTH_DOMAIN"],
	)