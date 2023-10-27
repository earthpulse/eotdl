from ...repos import UserDBRepo
from ...errors import UserDoesNotExistError
from ...models import User

def check_user_exists(uid: str) -> User:
    repo = UserDBRepo()
    if not repo.check_user_exists(uid):
        raise UserDoesNotExistError()