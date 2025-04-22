from ..datasets import retrieve_datasets
from ..models import retrieve_models

def retrieve_stac_collections():
    datasets = retrieve_datasets()
    data = [{'name': d.name, 'id': d.id} for d in datasets]
    models = retrieve_models()
    data.extend([{'name': m.name, 'id': m.id} for m in models])
    return data