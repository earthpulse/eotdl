from pydantic import BaseModel
from datetime import datetime
from ...models import User
from ...models.user import TermsAndConditions
from ...errors import UserDoesNotExistError


class RetrieveCredentials:
    def __init__(self, db_repo, eox_repo):
        self.db_repo = db_repo
        self.eox_repo = eox_repo

    class Inputs(BaseModel):
        uid: str
        email: str

    class Outputs(BaseModel):
        credentials: dict

    def __call__(self, inputs: Inputs) -> Outputs:
        # check user exists
        data = self.db_repo.retrieve("users", inputs.uid, "uid")
        if data is None:
            raise UserDoesNotExistError()
        # retrieve credentials
        data, error = self.eox_repo.retrieve_credentials(inputs.email)
        if error:
            raise Exception(error)
        return self.Outputs(credentials=data)
