from pydantic import BaseModel

class Logout():
    def __init__(self, repo):
        self.repo = repo

    class Inputs(BaseModel):
        redirect_uri: str

    class Outputs(BaseModel):
        logout_url: str

    def __call__(self, inputs: Inputs) -> Outputs:
        logout_url = self.repo.generate_logout_url(inputs.redirect_uri)
        return self.Outputs(logout_url=logout_url)