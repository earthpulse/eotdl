from pydantic import BaseModel

class Logout:
    def __init__(self, repo, api_repo):
        self.repo = repo
        self.api_repo = api_repo

    class Inputs(BaseModel):
        pass 

    class Outputs(BaseModel):
        logout_url: str

    def __call__(self, inputs: Inputs) -> Outputs:
        self.repo.logout()
        logout_url = self.api_repo.logout_url()
        return self.Outputs(logout_url=logout_url)