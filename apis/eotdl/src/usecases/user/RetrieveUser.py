from pydantic import BaseModel
from ...models import User 
from ...errors import UserDoesNotExistError

class RetrieveUser():
    def __init__(self, db_repo):
        self.db_repo = db_repo

    class Inputs(BaseModel):
        uid: str

    class Outputs(BaseModel):
        user: User

    def __call__(self, inputs: Inputs) -> Outputs:
        data = self.db_repo.retrieve('users', inputs.uid, 'uid')
        if data is None:
            raise UserDoesNotExistError()
        user = User(**data)
        return self.Outputs(user=user)
