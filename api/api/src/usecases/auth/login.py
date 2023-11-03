from ...repos import AuthRepo


def generate_login_url():
    repo = AuthRepo()
    return repo.generate_login_url()
