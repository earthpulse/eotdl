from xcube_geodb.core.geodb import GeoDBClient
import os
from .utils import validate_credentials


def get_client(credentials):
    validate_credentials(credentials)
    return GeoDBClient(
        server_url=credentials["GEODB_API_SERVER_URL"],
        server_port=credentials["GEODB_API_SERVER_PORT"],
        client_id=credentials["GEODB_AUTH_CLIENT_ID"],
        client_secret=credentials["GEODB_AUTH_CLIENT_SECRET"],
        auth_aud=credentials["GEODB_AUTH_DOMAIN"],
    )
