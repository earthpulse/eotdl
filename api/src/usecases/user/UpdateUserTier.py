from pydantic import BaseModel
from datetime import datetime
from ...models import User 
from ...errors import UserDoesNotExistError

class UpdateUserTier():
    def __init__(self, db_repo):
        self.db_repo = db_repo

    class Inputs(BaseModel):
        uid: str
        tier: str

    class Outputs(BaseModel):
        user: User

    def __call__(self, inputs: Inputs) -> Outputs:
        # check user exists
        data = self.db_repo.retrieve('users', inputs.uid, 'uid')
        if data is None:
            raise UserDoesNotExistError()
        # update user
        data.update(
            tier = inputs.tier,
            updatedAt = datetime.now()
        )
        user = User(**data)
        self.db_repo.update('users', data['_id'], user.dict())
        return self.Outputs(user=user)

