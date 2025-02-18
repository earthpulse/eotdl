from ...models import Change
from ...repos import ChangesDBRepo

def retrieve_change(change_id, user = None):
    repo = ChangesDBRepo()
    data = repo.retrieve_change(change_id)
    return Change(**data)
