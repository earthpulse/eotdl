from pydantic import BaseModel

class ParseToken():
    def __init__(self, repo):
        self.repo = repo

    class Inputs(BaseModel):
        token: str

    class Outputs(BaseModel):
        payload: dict

    def __call__(self, inputs: Inputs) -> Outputs:
        data = self.repo.parse_token(inputs.token)
        return self.Outputs(payload=data)