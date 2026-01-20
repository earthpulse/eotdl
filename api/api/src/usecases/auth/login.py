from ...repos import AuthRepo


def generate_login_url(redirect_uri):
    repo = AuthRepo()
    return repo.generate_login_url(redirect_uri)
