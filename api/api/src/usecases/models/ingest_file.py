from .retrieve_model import retrieve_owned_model
from ...repos import OSRepo

async def ingest_model_file(file_name, model_id, user):
    model = retrieve_owned_model(model_id, user.uid)
    os_repo = OSRepo()
    presigned_url = os_repo.generate_presigned_put_url(model_id, file_name)
    return presigned_url