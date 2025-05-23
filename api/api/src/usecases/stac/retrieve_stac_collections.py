from ..datasets import retrieve_datasets
from ..models import retrieve_models
from ..pipelines import retrieve_pipelines

def retrieve_stac_collections():
    datasets = retrieve_datasets()
    data = [{'name': d.name, 'id': d.id} for d in datasets]
    models = retrieve_models()
    data.extend([{'name': m.name, 'id': m.id} for m in models])
    pipelines = retrieve_pipelines()
    data.extend([{'name': p.name, 'id': p.id} for p in pipelines])
    return data