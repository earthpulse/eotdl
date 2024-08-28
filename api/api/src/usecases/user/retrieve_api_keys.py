from typing import List

from ...repos import UserDBRepo
from ...models import ApiKey, User


def retrieve_api_keys(user: User) -> List[ApiKey]:
    repo = UserDBRepo()
    keys = repo.retrieve_keys(user.uid)
    return [ApiKey(**key) for key in keys]
