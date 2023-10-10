import requests
import os


class AuthAPIRepo:
    def __init__(self, url=os.getenv("EOTDL_API_URL", "https://api.eotdl.com/")):
        # def __init__(self, url=os.getenv("EOTDL_API_URL", "http://localhost:8010/")):
        self.url = url

    def login(self):
        return requests.get(self.url + "auth/login")

    def token(self, code):
        return requests.get(self.url + "auth/token?code=" + code)

    def logout_url(self):
        response = requests.get(self.url + "auth/logout")
        return response.json()["logout_url"]

    def retrieve_credentials(self, id_token):
        response = requests.get(
            self.url + "auth/credentials",
            headers={"Authorization": "Bearer " + id_token},
        )
        if response.status_code == 200:
            return response.json(), None
        return None, response.json()["detail"]
