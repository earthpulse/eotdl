from ...repos import AuthRepo

def generate_id_token(code):
    repo = AuthRepo()
    return repo.generate_id_token(code)