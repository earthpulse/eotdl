from ...models import Change
from ...repos import ChangesDBRepo

def retrieve_change(id):
    repo = ChangesDBRepo()
    data = repo.retrieve_change(id)
    return Change(**data)
