import json

from ...repos import OSRepo

def stage_pipeline_file(pipeline_id, filename, user, version=None):
    os_repo = OSRepo()
    if not os_repo.exists(pipeline_id, filename):
        raise Exception(f"File `{filename}` does not exist")
    return os_repo.get_presigned_url(pipeline_id, filename)

def read_file(pipeline_id, filename, version=None):
    os_repo = OSRepo()
    if not os_repo.exists(pipeline_id, filename):
        raise Exception(f"File `{filename}` does not exist")
    if not filename.endswith('.json'):
        raise Exception(f"File `{filename}` is not a JSON file")
    content = os_repo.read_file(pipeline_id, filename)
    return json.loads(content.read().decode('utf-8'))