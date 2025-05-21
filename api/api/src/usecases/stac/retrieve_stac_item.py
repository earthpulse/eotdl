import pandas as pd

from ..datasets.retrieve_dataset import retrieve_dataset_by_name
from ..models.retrieve_model import retrieve_model_by_name
from ...errors import DatasetDoesNotExistError
from ...repos import OSRepo

# TODO: versioning

def retrieve_stac_item(collection_name, item_id, version):
    try:
        data = retrieve_dataset_by_name(collection_name)
    except DatasetDoesNotExistError:
        data = retrieve_model_by_name(collection_name)
    os_repo = OSRepo()
    catalog_presigned_url = os_repo.get_presigned_url(data.id, f"catalog.v{version}.parquet")
    # this read the entire catalog into memory, which is not ideal
    df = pd.read_parquet(catalog_presigned_url)
    # find items
    item = df[df["id"] == item_id]
    if item.empty:
        raise Exception(f"Item {item_id} not found in collection {collection_name}")
    return item.to_dict('records')[0] # should use stac-geoparquet to encode geometry correctly
