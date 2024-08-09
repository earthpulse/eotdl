from ...repos import UserDBRepo
from ...models import ApiKey, User
from .retrieve_api_keys import retrieve_api_keys


def create_api_key(user: User) -> ApiKey:
    repo = UserDBRepo()
    if len(retrieve_api_keys(user)) >= 5:
        raise Exception(
            "API key limit reached. Delete an existing key to create a new one."
        )
    key = repo.generate_id()
    key = ApiKey(id=key, uid=user.uid)
    repo.persist_key(key.model_dump())
    return key
