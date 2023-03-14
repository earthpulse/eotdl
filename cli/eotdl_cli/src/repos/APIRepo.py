import requests

class APIRepo():
    def __init__(self, url='http://localhost:8000/'):
        self.url = url

    def login(self):
        return requests.get(self.url + 'auth/login')
    
    def token(self, code):
        return requests.get(self.url + 'auth/token?code=' + code)

    def logout_url(self):
        response = requests.get(self.url + 'auth/logout')
        return response.json()['logout_url']