from ...repos import STACAPIRepo

def api_status():
    repo = STACAPIRepo()
    data, error = repo.status()
    if error:
        raise Exception(error)
    return data