from pydantic import BaseModel

class Login():
    def __init__(self, repo):
        self.repo = repo

    class Inputs(BaseModel):
        pass

    class Outputs(BaseModel):
        login_url: dict

    def __call__(self, inputs: Inputs) -> Outputs:
        login_url = self.repo.generate_login_url()
        return self.Outputs(login_url=login_url)