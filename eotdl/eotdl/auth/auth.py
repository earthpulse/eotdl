import time
import os

from ..repos import AuthRepo, AuthAPIRepo
from .errors import LoginError, AuthTimeOut
from .is_logged import is_logged


def auth(max_t=60, interval=2):
    user = is_logged()
    if user:
        return user
    repo, api_repo = AuthRepo(), AuthAPIRepo()
    api_key = os.environ.get("EOTDL_API_KEY", None)
    if api_key:
        print("Using API Key")
        user = {"api_key": api_key}
        user_data, error = api_repo.retrieve_user_data(user)
        if error:
            raise LoginError()
        user.update({"email": user_data["email"], "uid": user_data["uid"]})
    else:
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
                user = repo.decode_token(token_data)
                authenticated = True
                user = {
                    "id_token": token_data["id_token"],
                    "email": user["email"],
                    "uid": user["sub"],
                }
            else:
                time.sleep(interval)
        if not authenticated:
            raise AuthTimeOut()
    # get user credentials
    credentials = api_repo.retrieve_credentials(user)[0]
    if credentials:
        user.update(credentials)
    # save token data in file
    creds_path = repo.save_creds(user)
    print("Saved credentials to: ", creds_path)
    return user


# auth decorator
def with_auth(func):
    def wrapper(*args, **kwargs):
        user = auth()
        return func(*args, **kwargs, user=user)

    return wrapper
