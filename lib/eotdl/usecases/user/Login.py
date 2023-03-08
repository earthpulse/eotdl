from datetime import datetime
from pydantic import BaseModel

from ...models.user import User


class Login():
    def __init__(self, repo):
        self.repo = repo

    class Inputs(BaseModel):
        pass

    class Outputs(BaseModel):
        token: str

    def __call__(self, inputs: Inputs) -> Outputs:
        login_url = self.repo.generate_login_url()
        return self.Outputs(token=login_url)