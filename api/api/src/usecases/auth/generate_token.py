from ...repos import AuthRepo


def generate_id_token(code):
    repo = AuthRepo()
    return repo.generate_id_token(code)


def exchange_code_for_tokens(code, code_verifier, redirect_uri):
    repo = AuthRepo()
    return repo.exchange_code_for_tokens(code, code_verifier, redirect_uri)
