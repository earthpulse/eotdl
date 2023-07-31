from ...repos import DBRepo, EOXRepo
from ...models import User
from .PersistUser import PersistUser
from .UpdateUser import UpdateUser
from .RetrieveUser import RetrieveUser
from .RetrieveCredentials import RetrieveCredentials
from .AcceptTermsAndConditions import AcceptTermsAndConditions


def persist_user(data: dict) -> User:
    repo = DBRepo()
    persist_user = PersistUser(repo)
    inputs = PersistUser.Inputs(data=data)
    outputs = persist_user(inputs)
    return outputs.user


def update_user(user: User, data: dict) -> User:
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


def accept_user_terms_and_conditions(user):
    repo = DBRepo()
    eox_repo = EOXRepo()
    accept = AcceptTermsAndConditions(repo, eox_repo)
    inputs = AcceptTermsAndConditions.Inputs(uid=user.uid, email=user.email)
    outputs = accept(inputs)
    return outputs.user


def retrieve_user_credentials(user):
    repo = DBRepo()
    eox_repo = EOXRepo()
    retrieve = RetrieveCredentials(repo, eox_repo)
    inputs = RetrieveCredentials.Inputs(uid=user.uid, email=user.email)
    outputs = retrieve(inputs)
    return outputs.credentials
