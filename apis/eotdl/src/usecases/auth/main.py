from .Login import Login
from .GenerateToken import GenerateToken
from .ParseToken import ParseToken
from .Logout import Logout


from ...repos import AuthRepo


def generate_login_url():
    repo = AuthRepo()
    login = Login(repo)
    inputs = Login.Inputs()
    outputs = login(inputs)
    return outputs.login_url


def generate_id_token(code):
    repo = AuthRepo()
    generate_token = GenerateToken(repo)
    inputs = GenerateToken.Inputs(code=code)
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
