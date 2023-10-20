import time

from ..repos import AuthRepo, AuthAPIRepo
from .errors import LoginError, AuthTimeOut
from .is_logged import is_logged


def auth(max_t=30, interval=2):
    user = is_logged()
    if user:
        return user
    repo, api_repo = AuthRepo(), AuthAPIRepo()
    response = api_repo.login()
    if response.status_code != 200:
        raise LoginError()
    data = response.json()
    print("On your computer or mobile device navigate to: ", data["login_url"])
    authenticated = False
    t0 = time.time()
    while not authenticated and time.time() - t0 < max_t:
        response = api_repo.token(data["code"])
        token_data = response.json()
        if response.status_code == 200:
            print("Authenticated!")
            print("- Id Token: {}...".format(token_data["id_token"][:10]))
            # get user credentials
            credentials = api_repo.retrieve_credentials(token_data["id_token"])[0]
            token_data.update(credentials)
            # save token data in file
            creds_path = repo.save_creds(token_data)
            print("Saved credentials to: ", creds_path)
            current_user = repo.decode_token(token_data)
            authenticated = True
            current_user["id_token"] = token_data["id_token"]
            return current_user
        else:
            time.sleep(interval)
    if not authenticated:
        raise AuthTimeOut()


# auth decorator
def with_auth(func):
    def wrapper(*args, **kwargs):
        user = auth()
        return func(*args, **kwargs, user=user)

    return wrapper
