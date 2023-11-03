from ...repos import AuthRepo

def parse_token(token):
    repo = AuthRepo()
    return repo.parse_token(token)