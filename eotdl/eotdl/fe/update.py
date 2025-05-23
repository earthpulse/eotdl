from ..repos import FEAPIRepo
from ..auth import with_auth
from .retrieve import retrieve_pipeline

@with_auth
def deactivate_pipeline(pipeline_name, user):
    pipeline = retrieve_pipeline(pipeline_name)
    repo = FEAPIRepo()
    data, error = repo.deactivate_pipeline(pipeline['id'], user)
    if error:
        raise Exception(error)
    return data
