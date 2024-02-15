import os


class APIRepo:
    def __init__(self, url=None):
        default_url = "https://api.eotdl.com/"
        # default_url = "http://localhost:8010/"
        self.url = url if url else os.getenv("EOTDL_API_URL", default_url)

    def format_response(self, response):
        if response.status_code == 200:
            return response.json(), None
        return None, response.json()["detail"]

    def generate_headers(self, data):
        if "api_key" in data:
            return {"X-API-Key": data["api_key"]}
        if "id_token" in data:
            return {"Authorization": "Bearer " + data["id_token"]}
        raise Exception("Invalid headers")
