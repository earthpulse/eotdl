from ...models import User
from .PersistUser import PersistUser
from ...repos import MongoRepo

# save user info in db 
def persist_user(data: dict) -> User:
    repo = MongoRepo()
    persist_user = PersistUser(repo)
    inputs = PersistUser.Inputs(data=data)
    outputs = persist_user(inputs)
    return outputs.user