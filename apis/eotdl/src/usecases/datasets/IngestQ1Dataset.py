from pydantic import BaseModel


class IngestQ1Dataset:
    def __init__(self, db_repo, geodb_repo):
        self.db_repo = db_repo
        self.geodb_repo = geodb_repo

    class Inputs(BaseModel):
        dataset: str
        uid: str

    class Outputs(BaseModel):
        message: str

    def __call__(self, inputs: Inputs) -> Outputs:
        return self.Outputs(message="TODO: implement")
