from xcube_geodb.core.geodb import GeoDBClient
import os


def get_client():
    return GeoDBClient(
        server_url=os.environ["GEODB_SERVER_URL"],
        server_port=os.environ["GEODB_SERVER_PORT"],
        client_id=os.environ["GEODB_CLIENT_ID"],
        client_secret=os.environ["GEODB_CLIENT_SECRET"],
        auth_aud=os.environ["GEODB_AUTH_DOMAIN"],
    )
