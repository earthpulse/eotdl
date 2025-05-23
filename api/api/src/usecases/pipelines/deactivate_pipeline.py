from ...repos import PipelinesDBRepo
from .retrieve_pipeline import retrieve_owned_pipeline

def deactivate_pipeline(pipeline_id, user):
    pipeline = retrieve_owned_pipeline(pipeline_id, user.uid)
    repo = PipelinesDBRepo()
    repo.deactivate_pipeline(pipeline_id)
    return f"Pipeline {pipeline_id} has been deactivated."