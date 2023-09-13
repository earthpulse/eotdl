from pydantic import BaseModel
from typing import Union


class IsLogged:
    def __init__(self, repo):
        self.repo = repo

    class Inputs(BaseModel):
        pass

    class Outputs(BaseModel):
        user: Union[dict, None]

    def __call__(self, inputs: Inputs) -> Outputs:
        user = self.repo.load_creds()
        return self.Outputs(user=user)
