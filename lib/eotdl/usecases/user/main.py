from ...models import User
from .Login import Login
from .PersistUser import PersistUser
from ...repos import MongoRepo, AuthRepo

# retrieve user token
def login() -> str:
    repo = AuthRepo()
    login = Login(repo)
    inputs = Login.Inputs()
    outputs = login(inputs)
    return outputs.token

# save user info in db 
def persist_user(data: dict) -> User:
    repo = MongoRepo()
    persist_user = PersistUser(repo)
    inputs = PersistUser.Inputs(data=data)
    outputs = persist_user(inputs)
    return outputs.user
