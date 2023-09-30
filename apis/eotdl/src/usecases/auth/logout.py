from ...repos import AuthRepo

def generate_logout_url(redirect_uri):
    repo = AuthRepo()
    return repo.generate_logout_url(redirect_uri)