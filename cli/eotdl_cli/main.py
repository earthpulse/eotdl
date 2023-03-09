import typer
import requests
import time
import jwt
import os 
import json 
from pathlib import Path

ALGORITHMS = ['RS256']
API_URL = 'http://localhost:8000/'
home = str(Path.home())
creds_path = home + '/.etodl/creds.json'

app = typer.Typer()

def is_logged():
    if os.path.exists(creds_path):
        with open(creds_path, 'r') as f:
            creds = json.load(f)
        current_user = jwt.decode(creds['id_token'], algorithms=ALGORITHMS, options={"verify_signature": False})    
        return current_user
    else:
        return False

def auth():
    user = is_logged()
    if user:
        return user
    response = requests.get(API_URL + 'auth/login')
    if response.status_code != 200:
        print('login error')
        raise typer.Exit(code=1)
    data = response.json()
    print('On your computer or mobile device navigate to: ', data['login_url'])
    authenticated = False
    t0 = time.time()
    max_t = 30
    while not authenticated and time.time() - t0 < max_t:
        response = requests.get(API_URL + 'auth/token?code=' + data['code'])
        token_data = response.json()
        if response.status_code == 200:
            print('Authenticated!')
            print('- Id Token: {}...'.format(token_data['id_token'][:10]))
            # save token data in file
            os.makedirs(home + '/.etodl', exist_ok=True)
            with open(creds_path, 'w') as f:
                json.dump(token_data, f)
            print('Saved credentials to: ', creds_path)
            current_user = jwt.decode(token_data['id_token'], algorithms=ALGORITHMS, options={"verify_signature": False})
            authenticated = True
            return current_user
        else:
            time.sleep(2)
    if not authenticated:
        print('Authentication timed out')
        raise typer.Exit(code=1)

@app.callback()
def callback():
    pass


@app.command()
def hello(name: str = 'World!'):
    """Say hello to someone"""
    typer.echo(f"hello, {name}")


@app.command()
def login():
    user = auth()
    typer.echo(f"You are logged in as {user['email']}")

@app.command()
def logout():
    user = is_logged()
    if user:
        typer.echo(f"You are logged in as {user['email']}")
        typer.confirm(f"Are you sure you want to logout?", abort=True)
        os.remove(creds_path)
        response = requests.get(API_URL + 'auth/logout')
        logout_url = response.json()['logout_url']
        typer.echo(f"You are logged out.")
        typer.echo(f"If you want to login with a different account, visit {logout_url} and login again.")
    else:
        typer.echo(f"You are not logged in.")

if __name__ == "__main__":
    app()