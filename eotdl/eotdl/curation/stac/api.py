import json

from ...repos import STACAPIRepo

def api_status():
    repo = STACAPIRepo()
    data, error = repo.status()
    if error:
        raise Exception(error)
    return data

def retrieve_stac_collections():
    repo = STACAPIRepo()
    data, error = repo.collections()
    if error:
        raise Exception(error)
    return data

def retrieve_stac_collection(collection_name):
    repo = STACAPIRepo()
    data, error = repo.collection(collection_name)
    if error:
        raise Exception(error)
    return data

def retrieve_stac_items(collection_id):
    repo = STACAPIRepo()
    data, error = repo.items(collection_id)
    if error:
        raise Exception(error)
    return data

def retrieve_stac_item(collection_id, item_id):
    repo = STACAPIRepo()
    data, error = repo.item(collection_id, item_id)
    if error:
        raise Exception(error)
    return data

def search_stac_items(collection_id, query = None):
    repo = STACAPIRepo()
    if query is None:
        data, error = repo.search_columns(collection_id)
        if error:
            raise Exception(error)
        return data
    data, error = repo.search(collection_id, str(query))
    if error:
        raise Exception(error)
    return json.loads(data)
    

def search_stac_columns(collection_id):
    repo = STACAPIRepo()
    data, error = repo.search_columns(collection_id)
    if error:
        raise Exception(error)
    return data
