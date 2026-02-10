from ...repos import AuthDBRepo


def update_auth_state(state, code):
    repo = AuthDBRepo()
    return repo.update_auth_state(state, code)
