from datetime import datetime
import re

from ...repos import UserDBRepo
from ...errors import UserAlreadyExistsError, NameCharsValidationError, NameLengthValidationError
from ...models import User 
from .retrieve_user import retrieve_user

# we do it here instead of in model because first time a user is created, the name comes from auth0 and is usually an email
def validate_name(name: str, regex: str = "^[^a-zA-Z]{1}|[^a-zA-Z0-9-]", max_length: int = 15, min_length: int = 3) -> str:
    if re.findall(regex, name):
        raise NameCharsValidationError()
    if len(name) > max_length or len(name) < min_length:
        raise NameLengthValidationError(max_length, min_length)
    return name

def update_user(user: User, data: dict) -> User:
    repo = UserDBRepo()
    # check user exists
    user_data = retrieve_user(user.uid).model_dump()
    # check new name is unique
    if 'name' in data:
        if repo.find_one_user_by_name(data['name']) is not None:
            raise UserAlreadyExistsError()
        # validate name 
        validate_name(data['name'])
    # update user
    user_data.update(
        name = data['name'] if 'name' in data else user_data['name'],
        updatedAt = datetime.now()
    )
    user = User(**user_data)
    repo.update_user(user_data['id'], user.model_dump())
    return user

