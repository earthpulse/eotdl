import requests
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

    def retrieve_credentials(self, auth):
        response = requests.get(
            self.url + "auth/credentials",
            headers=self.generate_headers(auth),
        )
        if response.status_code == 200:
            return response.json(), None
        return None, response.json()["detail"]

    def retrieve_user_data(self, auth):
        response = requests.get(
            self.url + "auth/me",
            headers=self.generate_headers(auth),
        )
        return self.format_response(response)
