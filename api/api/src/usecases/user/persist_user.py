from datetime import datetime

from ...models.user import User
from ...repos import UserDBRepo
from .retrieve_user import retrieve_user
from ...errors import UserDoesNotExistError

def persist_user(data: dict) -> User:
    repo = UserDBRepo()
    try:
        user = retrieve_user(data["uid"]).model_dump()
        # Do not overwrite profile edits on each login; only fill missing fields.
        if not user.get("name") and data.get("name"):
            user["name"] = data.get("name")
        if not user.get("picture") and data.get("picture"):
            user["picture"] = data.get("picture")
        user.update(
            email=data["email"],
            updatedAt=datetime.now(),
        )
        updated_user = User(**user)
        repo.update_user(user["id"], updated_user.model_dump())
        return updated_user
    except UserDoesNotExistError:
        data["id"] = repo.generate_id()
        new_user = User(**data)
        repo.persist_user(new_user.model_dump(), new_user.id)
        return new_user
