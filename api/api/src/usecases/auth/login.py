from ...repos import AuthRepo, AuthDBRepo


def generate_login_url(redirect_uri):
    repo, db_repo = AuthRepo(), AuthDBRepo()
    response = repo.generate_login_url(redirect_uri)
    state = response.get("state")
    code_verifier = response.get("code_verifier")
    if state and code_verifier:
        db_repo.create_auth_state(
            {"state": state, "code_verifier": code_verifier, "code": None}
        )
        return response
    raise Exception("Failed to generate login URL")
