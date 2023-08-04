from pydantic import BaseModel
from datetime import datetime
from ...models import User
from ...models.user import TermsAndConditions
from ...errors import UserDoesNotExistError


class AcceptTermsAndConditions:
    def __init__(self, db_repo, eox_repo):
        self.db_repo = db_repo
        self.eox_repo = eox_repo

    class Inputs(BaseModel):
        uid: str
        email: str

    class Outputs(BaseModel):
        user: User

    def __call__(self, inputs: Inputs) -> Outputs:
        # check user exists
        data = self.db_repo.retrieve("users", inputs.uid, "uid")
        if data is None:
            raise UserDoesNotExistError()
        # generate credentials
        errors = self.eox_repo.generate_credentials(inputs.uid, inputs.email)
        if len(errors) > 0:
            raise Exception(errors)
        # update user
        data.update(
            terms=TermsAndConditions(
                geodb=True, sentinelhub=True, eotdl=True, eoxhub=True
            ),
            updatedAt=datetime.now(),
        )
        user = User(**data)
        self.db_repo.update("users", data["_id"], user.dict())
        return self.Outputs(user=user)
