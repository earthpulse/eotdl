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
            print(data)
            response = requests.post(
                self.provisionings_url, headers=headers, data=json.dumps(data)
            )
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
        print(response.json())
        if response.status_code != 200:
            return response.json(), None
        return None, response.json()

    def get_vault_token(self):
        headers = {"Content-Type": "application/json"}
        response = requests.get(
            f"{self.vault_url}/auth/approle/login",
            headers=headers,
            data={"role_id": self.vault_role_id, "secret_id": self.vault_secret_id},
        )
        print("TOKEN", response.json())
        if response.status_code != 200:
            return response.json()["client_token"], None
        return None, response.json()
