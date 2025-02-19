from ..datasets import retrieve_datasets

def retrieve_stac_collections():
    datasets = retrieve_datasets()
    return [d.name for d in datasets]