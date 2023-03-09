import typer
import requests
import time
from auth0.authentication.token_verifier import TokenVerifier, AsymmetricSignatureVerifier
import jwt
import os 
import json 
from pathlib import Path

AUTH0_DOMAIN = 'earthpulse.eu.auth0.com'
AUTH0_CLIENT_ID = 'sC5WflzmPoj058FJYL2ckENutxJL4PTW'
ALGORITHMS = ['RS256']

app = typer.Typer()

def login():
    home = str(Path.home())
    creds_path = home + '/.etodl/creds.json'
    # check if creds exist
    if os.path.exists(creds_path):
        with open(creds_path, 'r') as f:
            creds = json.load(f)
        validate_token(creds['id_token'])
        current_user = jwt.decode(creds['id_token'], algorithms=ALGORITHMS, options={"verify_signature": False})    
        return current_user
    # if not, retrieve them from auth0
    device_code_payload = {
        'client_id': AUTH0_CLIENT_ID,
        'scope': 'openid profile email'
    }
    device_code_response = requests.post('https://{}/oauth/device/code'.format(AUTH0_DOMAIN), data=device_code_payload)
    if device_code_response.status_code != 200:
        print('Error generating the device code')
        raise typer.Exit(code=1)
    print('Device code successful')
    device_code_data = device_code_response.json()
    print('1. On your computer or mobile device navigate to: ', device_code_data['verification_uri_complete'])
    print('2. Enter the following code: ', device_code_data['user_code'])
    token_payload = {
        'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
        'device_code': device_code_data['device_code'],
        'client_id': AUTH0_CLIENT_ID
    }
    authenticated = False
    while not authenticated:
        print('Checking if the user completed the flow...')
        token_response = requests.post('https://{}/oauth/token'.format(AUTH0_DOMAIN), data=token_payload)
        token_data = token_response.json()
        if token_response.status_code == 200:
            print('Authenticated!')
            print('- Id Token: {}...'.format(token_data['id_token'][:10]))
            validate_token(token_data['id_token'])
            # save token data in fileç
            with open(creds_path, 'w') as f:
                json.dump(token_data, f)
            current_user = jwt.decode(token_data['id_token'], algorithms=ALGORITHMS, options={"verify_signature": False})
            authenticated = True
            return current_user
        elif token_data['error'] not in ('authorization_pending', 'slow_down'):
            print(token_data['error_description'])
            raise typer.Exit(code=1)
        else:
            time.sleep(device_code_data['interval'])

def validate_token(id_token):
    """
    Verify the token and its precedence

    :param id_token:
    """
    jwks_url = 'https://{}/.well-known/jwks.json'.format(AUTH0_DOMAIN)
    issuer = 'https://{}/'.format(AUTH0_DOMAIN)
    sv = AsymmetricSignatureVerifier(jwks_url)
    tv = TokenVerifier(signature_verifier=sv, issuer=issuer, audience=AUTH0_CLIENT_ID)
    tv.verify(id_token)

@app.callback()
def callback():
    pass


@app.command()
def hello(name: str = 'World!'):
    """Say hello to someone"""
    user = login()
    print(user)
    typer.echo(f"hello, {name}")

if __name__ == "__main__":
    app()