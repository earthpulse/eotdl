from ...repos import UserDBRepo
from ...models import User
from ...errors import InvalidApiKey


def delete_api_key(user: User, key: str) -> str:
    repo = UserDBRepo()
    key = repo.retrieve_user_by_key(key)
    if not key or key["uid"] != user.uid:
        raise InvalidApiKey()
    repo.delete_key(key["id"])
    return "Key deleted"
