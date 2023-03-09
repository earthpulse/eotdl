from pydantic import BaseModel

class GenerateToken():
    def __init__(self, repo):
        self.repo = repo

    class Inputs(BaseModel):
        code: str

    class Outputs(BaseModel):
        token: dict

    def __call__(self, inputs: Inputs) -> Outputs:
        token = self.repo.generate_id_token(inputs.code)
        return self.Outputs(token=token)