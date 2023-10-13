import requests
import os
from .APIRepo import APIRepo


class AuthAPIRepo(APIRepo):
    def __init__(self, url=None):
        super().__init__(url)

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
