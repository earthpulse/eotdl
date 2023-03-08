from pydantic import BaseModel

class Login():
    def __init__(self, repo):
        self.repo = repo

    class Inputs(BaseModel):
        redirect_uri: str
        goto: str = None

    class Outputs(BaseModel):
        login_url: str

    def __call__(self, inputs: Inputs) -> Outputs:
        login_url = self.repo.generate_login_url(inputs.redirect_uri, inputs.goto)
        return self.Outputs(login_url=login_url)