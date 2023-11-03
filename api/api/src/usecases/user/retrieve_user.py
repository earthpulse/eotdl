from ...repos import UserDBRepo
from ...errors import UserDoesNotExistError
from ...models import User

def retrieve_user(uid: str) -> User:
    repo = UserDBRepo()
    user = repo.retrieve_user_by_uid(uid)
    if user is None:
        raise UserDoesNotExistError()
    return User(**user)