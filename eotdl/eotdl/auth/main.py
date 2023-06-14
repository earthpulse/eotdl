from ..src.repos import AuthRepo, APIRepo
from ..src.usecases.auth import IsLogged, Auth, Logout


def is_logged():
    repo = AuthRepo()
    _is_logged = IsLogged(repo)
    inputs = _is_logged.Inputs()
    outputs = _is_logged(inputs)
    return outputs.user


def auth():
    user = is_logged()
    if user:
        return user
    api_repo = APIRepo()
    repo = AuthRepo()
    _auth = Auth(repo, api_repo)
    inputs = _auth.Inputs()
    outputs = _auth(inputs)
    return outputs.user


def generate_logout_url():
    api_repo = APIRepo()
    repo = AuthRepo()
    _logout = Logout(repo, api_repo)
    inputs = _logout.Inputs()
    outputs = _logout(inputs)
    return outputs.logout_url


# auth decorator
def with_auth(func):
    def wrapper(*args, **kwargs):
        user = auth()
        return func(*args, **kwargs, user=user)

    return wrapper
