from ..datasets import retrieve_dataset_by_name

def retrieve_stac_collection(collection_id):
    # Should be a STAC collection???
    return retrieve_dataset_by_name(collection_id)