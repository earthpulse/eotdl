from .Login import Login
from .GenerateToken import GenerateToken
from .ParseToken import ParseToken
from .Logout import Logout

from ...repos import AuthRepo

def generate_login_url(redirect_uri, goto):
    repo = AuthRepo()
    login = Login(repo)
    inputs = Login.Inputs(redirect_uri=redirect_uri, goto=goto)
    outputs = login(inputs)
    return outputs.login_url

def generate_id_token(code, redirect_uri):
    repo = AuthRepo()
    generate_token = GenerateToken(repo)
    inputs = GenerateToken.Inputs(code=code, redirect_uri=redirect_uri)
    outputs = generate_token(inputs)
    return outputs.token

def parse_token(token):
    repo = AuthRepo()
    parse = ParseToken(repo)
    inputs = ParseToken.Inputs(token=token)
    outputs = parse(inputs)
    return outputs.payload

def generate_logout_url(redirect_uri):
    repo = AuthRepo()
    logout = Logout(repo)
    inputs = Logout.Inputs(redirect_uri=redirect_uri)
    outputs = logout(inputs)
    return outputs.logout_url