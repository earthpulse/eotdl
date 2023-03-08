from pydantic import BaseModel

class GenerateToken():
    def __init__(self, repo):
        self.repo = repo

    class Inputs(BaseModel):
        code: str
        redirect_uri: str

    class Outputs(BaseModel):
        token: str

    def __call__(self, inputs: Inputs) -> Outputs:
        token = self.repo.generate_id_token(inputs.code, inputs.redirect_uri)
        return self.Outputs(token=token['id_token'])