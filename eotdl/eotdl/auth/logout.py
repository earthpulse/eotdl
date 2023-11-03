from ..repos import AuthRepo, AuthAPIRepo


def logout_user():
    repo, api_repo = AuthRepo(), AuthAPIRepo()
    repo.logout()
    return api_repo.logout_url()
