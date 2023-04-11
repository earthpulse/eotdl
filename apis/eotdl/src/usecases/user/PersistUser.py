from datetime import datetime
from pydantic import BaseModel

from ...models.user import User


class PersistUser():
    def __init__(self, repo):
        self.repo = repo

    class Inputs(BaseModel):
        data: dict or None

    class Outputs(BaseModel):
        user: User

    def __call__(self, inputs: Inputs) -> Outputs:
        uid = inputs.data['uid']
        user = self.repo.retrieve('users', uid, 'uid')
        if user:
            user.update(
                # name=inputs.data['name'],
                # picture=inputs.data['picture'],
                email=inputs.data['email'],
                updatedAt=datetime.now()
            )
            updated_user = User(**user)
            self.repo.update('users', user['_id'], updated_user.dict())
            return self.Outputs(user=updated_user)
        new_user = User(**inputs.data)
        self.repo.persist('users', new_user.dict())
        return self.Outputs(user=User(**inputs.data))