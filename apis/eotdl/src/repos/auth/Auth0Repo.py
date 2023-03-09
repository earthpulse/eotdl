import jwt
import requests
import os
from auth0.authentication.token_verifier import TokenVerifier, AsymmetricSignatureVerifier

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

    def generate_login_url(self):
        device_code_payload = {
            'client_id': self.client_id,
            'scope': 'openid profile email'
        }
        device_code_response = requests.post('https://{}/oauth/device/code'.format(self.domain), data=device_code_payload)
        if device_code_response.status_code != 200:
            raise Exception('Error generating the device code')
        device_code_data = device_code_response.json()
        return {
            'login_url': device_code_data['verification_uri_complete'],
            'code': device_code_data['device_code'],
            'message': 'Navigate to the URL and confirm to login. Then, request your token at the /token endpoint with the provided code.'
        }

    def generate_id_token(self, code):
        token_payload = {
            'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
            'device_code': code,
            'client_id': self.client_id
        }
        token_response = requests.post('https://{}/oauth/token'.format(self.domain), data=token_payload)
        token_data = token_response.json()
        if token_response.status_code == 200:
            self.validate_token(token_data['id_token'])
            return {
                'id_token': token_data['id_token'],
                'expires_in': token_data['expires_in'],
                'token_type': token_data['token_type']
            }
        raise Exception(token_response.json()['error_description'])

    def validate_token(self, id_token):
        jwks_url = 'https://{}/.well-known/jwks.json'.format(self.domain)
        issuer = 'https://{}/'.format(self.domain)
        sv = AsymmetricSignatureVerifier(jwks_url)
        tv = TokenVerifier(signature_verifier=sv, issuer=issuer, audience=self.client_id)
        tv.verify(id_token)

    def parse_token(self, token):
        payload = jwt.decode(token, algorithms=self.algorithms, options={"verify_signature": False})
        return {
            'uid': payload['sub'],
            'name': payload['name'],
            'email': payload['email'],
            'picture': payload['picture'],
        }