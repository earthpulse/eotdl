import base64
import hashlib
import os
import secrets
from urllib.parse import urlencode

import jwt
import requests


class LogtoRepo:
    def __init__(self):
        self.domain = os.environ["LOGTO_DOMAIN"]
        self.client_id = os.environ["LOGTO_APP_ID"]
        self.client_secret = os.environ["LOGTO_APP_SECRET"]
        well_known = requests.get(
            f"https://{self.domain}/oidc/.well-known/openid-configuration", timeout=10
        ).json()
        self.issuer = well_known["issuer"]
        self.authz_endpoint = well_known["authorization_endpoint"]
        self.token_endpoint = well_known["token_endpoint"]
        self.jwks_uri = well_known["jwks_uri"]
        self.userinfo_endpoint = well_known.get("userinfo_endpoint")
        self.algorithms = ["RS256"]

    def generate_login_url(self, redirect_uri):
        code_verifier = (
            base64.urlsafe_b64encode(secrets.token_bytes(64)).rstrip(b"=").decode()
        )
        code_challenge = (
            base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest())
            .rstrip(b"=")
            .decode()
        )
        state = secrets.token_urlsafe(16)
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid profile email",
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "state": state,
        }
        return {
            "login_url": f"{self.authz_endpoint}?{urlencode(params)}",
            "state": state,
            "code_verifier": code_verifier,
        }

    def exchange_code_for_tokens(self, code, code_verifier, redirect_uri):
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "code_verifier": code_verifier,
        }
        response = requests.post(
            self.token_endpoint,
            data=data,
            auth=(self.client_id, self.client_secret),
            timeout=10,
        )
        response.raise_for_status()
        tokens = response.json()
        return {
            "id_token": tokens.get("id_token"),
            "token_type": tokens.get("token_type"),
            "expires_in": tokens.get("expires_in"),
        }

    def validate_token(self, id_token):
        jwks_resp = requests.get(self.jwks_uri, timeout=10)
        jwks_resp.raise_for_status()
        jwks = jwks_resp.json()
        unverified_header = jwt.get_unverified_header(id_token)
        key = None
        for jwk in jwks["keys"]:
            if jwk["kid"] == unverified_header["kid"]:
                key = jwt.algorithms.ECAlgorithm.from_jwk(jwk)
                break
        if key is None:
            raise Exception("Public key not found in JWKS")
        payload = jwt.decode(
            id_token,
            key=key,
            algorithms=["ES384"],
            audience=self.client_id,
            issuer=self.issuer,
        )
        return payload

    def parse_token(self, token):
        payload = jwt.decode(
            token, algorithms=self.algorithms, options={"verify_signature": False}
        )
        return {
            "uid": payload.get("sub"),
            "name": payload.get("name"),
            "email": payload.get("email"),
            "picture": payload.get("picture"),
        }

    def get_userinfo(self, access_token):
        r = requests.get(
            self.userinfo_endpoint,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        r.raise_for_status()
        return r.json()

    def generate_logout_url(self, post_logout_redirect_uri, id_token_hint=None):
        params = {"post_logout_redirect_uri": post_logout_redirect_uri}
        if id_token_hint:
            params["id_token_hint"] = id_token_hint
        return f"https://{self.domain}/oidc/session/end?{urlencode(params)}"
