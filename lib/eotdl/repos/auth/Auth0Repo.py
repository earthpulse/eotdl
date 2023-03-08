import jwt
import requests
import os

class Auth0Repo():
    def __init__(self):
        self.domain = os.environ['AUTH0_DOMAIN']
        self.client_id = os.environ['AUTH0_CLIENT_ID']
        self.client_secret = os.environ['AUTH0_CLIENT_SECRET']

        self.algorithms = ["RS256"]
        self.issuer = f"https://{self.domain}/"
        self.audience = f"https://{self.domain}/api/v2/"

        jwks_url = f'https://{self.domain}/.well-known/jwks.json'
        self.jwks_client = jwt.PyJWKClient(jwks_url)

    def generate_login_url(self, redirect_uri='/', goto=None):
        return f'https://{self.domain}/authorize?response_type=code&scope=openid profile email&client_id={self.client_id}&redirect_uri={redirect_uri}{f"?goto={goto}" if goto else ""}'

    def generate_id_token(self, code, redirect_uri):
        payload = {
            'client_id': self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri
        }
        res = requests.post(f"https://{self.domain}/oauth/token", json=payload)
        return res.json()

    def parse_token(self, token):
        signing_key = self.jwks_client.get_signing_key_from_jwt(
            token).key
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=self.algorithms,
            issuer=self.issuer,
            audience=self.client_id
        )
        return payload

    def generate_logout_url(self, redirect_uri):
        return f'https://{self.domain}/v2/logout?cliend_id={self.client_id}&returnTo={redirect_uri}'
