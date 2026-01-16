import jwt


class LogtoRepo:
    def __init__(self):
        self.algorithms = ["RS256"]

    def generate_login_url(self):
        raise NotImplementedError("Logto login is handled via the UI flow.")

    def generate_id_token(self, code):
        raise NotImplementedError("Logto token exchange is handled via the UI flow.")

    def validate_token(self, id_token):
        raise NotImplementedError("Token validation is handled by Logto in the UI.")

    def parse_token(self, token):
        payload = jwt.decode(
            token, algorithms=self.algorithms, options={"verify_signature": False}
        )
        return {
            "uid": payload["sub"],
            "name": payload.get("name"),
            "email": payload["email"],
            "picture": payload.get("picture"),
        }

    def generate_logout_url(self, redirect_uri):
        raise NotImplementedError("Logto logout is handled via the UI flow.")
