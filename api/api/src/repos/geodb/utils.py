def validate_credentials(credentials):
    if credentials is None:
        raise Exception("No credentials provided")
    fields = [
        "GEODB_API_SERVER_PORT",
        "GEODB_API_SERVER_URL",
        "GEODB_AUTH_AUD",
        "GEODB_AUTH_CLIENT_ID",
        "GEODB_AUTH_CLIENT_SECRET",
        "GEODB_AUTH_DOMAIN",
    ]
    for field in fields:
        if field not in credentials:
            raise Exception(f"Missing credential: {field}")
