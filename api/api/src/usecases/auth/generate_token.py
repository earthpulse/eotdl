from ...repos import AuthRepo, AuthDBRepo


def generate_id_token(code):
    repo = AuthRepo()
    return repo.generate_id_token(code)


def exchange_code_for_tokens(state, redirect_uri):
    repo, db_repo = AuthRepo(), AuthDBRepo()
    data = db_repo.retrieve_auth_state(state)
    if not data:
        db_repo.delete_auth_state(state)
        raise Exception("Auth state not found")
    code, code_verifier = data.get("code"), data.get("code_verifier")
    if not code:
        raise Exception("Code not found")
    tokens = repo.exchange_code_for_tokens(
        code=code,
        code_verifier=code_verifier,
        redirect_uri=redirect_uri,
    )
    db_repo.delete_auth_state(state)
    return tokens
