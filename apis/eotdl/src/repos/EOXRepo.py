import os
import requests
from enum import Enum
import json


class Service(Enum):
    SH = "sh"
    GEODB = "geodb"
    EOXHUB = "eoxhub"


class EOXRepo:
    def __init__(self):
        self.provisionings_url = os.environ.get("EOX_PROVISIONINGS_URL")
        self.vault_url = os.environ.get("EOX_VAULT_URL")
        self.vault_role_id = os.environ.get("EOX_VAULT_ROLE_ID")
        self.vault_secret_id = os.environ.get("EOX_VAULT_SECRET_ID")

    def generate_credentials(self, uid, email):
        headers = {"Content-Type": "application/json"}
        data = {"userName": uid, "email": email}
        services = [Service.SH, Service.GEODB, Service.EOXHUB]
        errors = []
        for service in services:
            data["serviceName"] = service.value
            response = requests.post(self.provisionings_url, headers=headers, data=data)
            print(response.status_code)
            if response.status_code != 201:
                print("ERROR", response.text)
                errors.append(response.text)
        return errors

    def retrieve_credentials(self, email):
        token, error = self.get_vault_token()
        if error:
            return None, error
        headers = {"X-Vault-Token": token}
        response = requests.get(f"{self.vault_url}/eotdl/data/{email}", headers=headers)
        if response.status_code != 200:
            return None, response.json()
        return response.json()["data"]["data"], None

    def get_vault_token(self):
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            f"{self.vault_url}/auth/approle/login",
            headers=headers,
            json={"role_id": self.vault_role_id, "secret_id": self.vault_secret_id},
        )
        if response.status_code != 200:
            return None, response.json()
        return response.json()["auth"]["client_token"], None
