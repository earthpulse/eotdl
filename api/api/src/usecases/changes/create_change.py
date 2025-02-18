from ...models import Change
from ...repos import ChangesDBRepo

def create_change(user, type, payload):
    changes_repo = ChangesDBRepo()
    change_id = changes_repo.generate_id()
    change = Change(
        id=change_id,
        uid=user.uid,
        type=type,
        payload=payload,
    )
    changes_repo.persist_change(change.model_dump(), change_id)
    return change