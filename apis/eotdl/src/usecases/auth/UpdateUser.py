from pydantic import BaseModel
from typing import List
from datetime import datetime
from ...models import User 
from ...errors import UserDoesNotExistError, UserAlreadyExistsError

class UpdateUser():
    def __init__(self, db_repo):
        self.db_repo = db_repo

    class Inputs(BaseModel):
        uid: str
        data: dict

    class Outputs(BaseModel):
        user: User

    def __call__(self, inputs: Inputs) -> Outputs:
        # check user exists
        data = self.db_repo.retrieve('users', inputs.uid, 'uid')
        if data is None:
            raise UserDoesNotExistError()
        # check new name is unique
        if 'name' in inputs.data:
            if self.db_repo.find_one_by_name('users', inputs.data['name']) is not None:
                raise UserAlreadyExistsError()
        # update user
        data.update(
            name = inputs.data['name'] if 'name' in inputs.data else data['name'],
            updatedAt = datetime.now()
        )
        user = User(**data)
        self.db_repo.update('users', data['_id'], user.dict())
        return self.Outputs(user=user)
