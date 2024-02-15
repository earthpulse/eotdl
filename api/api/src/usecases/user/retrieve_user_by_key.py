from ...repos import UserDBRepo
from ...errors import UserDoesNotExistError, InvalidApiKey
from ...models import User


def retrieve_user_by_key(api_key: str) -> User:
    repo = UserDBRepo()
    data = repo.retrieve_user_by_key(api_key)
    if data is None:
        raise InvalidApiKey()
    user = repo.retrieve_user_by_uid(data["uid"])
    if user is None:
        raise UserDoesNotExistError()
    return User(**user)
