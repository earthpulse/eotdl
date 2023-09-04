from ...models import User
from .PersistUser import PersistUser
from .UpdateUser import UpdateUser
from .RetrieveUser import RetrieveUser
from .UpdateUserTier import UpdateUserTier

from ...repos import DBRepo

def persist_user(data: dict) -> User:
    repo = DBRepo()
    persist_user = PersistUser(repo)
    inputs = PersistUser.Inputs(data=data)
    outputs = persist_user(inputs)
    return outputs.user

def update_user(user, data):
    repo = DBRepo()
    update = UpdateUser(repo)
    inputs = UpdateUser.Inputs(uid=user.uid, data=data)
    outputs = update(inputs)
    return outputs.user

def retrieve_user(user):
    repo = DBRepo()
    retrieve = RetrieveUser(repo)
    inputs = RetrieveUser.Inputs(uid=user.uid)
    outputs = retrieve(inputs)
    return outputs.user

def update_user_tier(uid, tier):
    repo = DBRepo()
    update = UpdateUserTier(repo)
    inputs = UpdateUserTier.Inputs(uid=uid, tier=tier)
    outputs = update(inputs)
    return outputs.user