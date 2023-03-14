from ...models import User
from .PersistUser import PersistUser
from ...repos import DBRepo

# save user info in db 
def persist_user(data: dict) -> User:
    repo = DBRepo()
    persist_user = PersistUser(repo)
    inputs = PersistUser.Inputs(data=data)
    outputs = persist_user(inputs)
    return outputs.user