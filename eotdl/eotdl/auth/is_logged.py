from ..repos import AuthRepo


def is_logged():
    repo = AuthRepo()
    user = repo.load_creds()
    return user
