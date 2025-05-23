from .retrieve_pipeline import retrieve_owned_pipeline
from ...repos import OSRepo

async def ingest_pipeline_file(file_name, pipeline_id, user):
    pipeline = retrieve_owned_pipeline(pipeline_id, user.uid)
    os_repo = OSRepo()
    presigned_url = os_repo.generate_presigned_put_url(pipeline_id, file_name)
    return presigned_url