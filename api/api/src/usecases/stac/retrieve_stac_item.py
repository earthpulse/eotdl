import pandas as pd

from ..datasets.retrieve_dataset import retrieve_dataset
from ..models.retrieve_model import retrieve_model
from ...errors import DatasetDoesNotExistError
from ...repos import OSRepo

# TODO: versioning

def retrieve_stac_item(collection_id, item_id, version):
    try:
        data = retrieve_dataset(collection_id)
    except DatasetDoesNotExistError:
        data = retrieve_model(collection_id)
    os_repo = OSRepo()
    catalog_presigned_url = os_repo.get_presigned_url(data.id, f"catalog.v{version}.parquet")
    # this read the entire catalog into memory, which is not ideal
    df = pd.read_parquet(catalog_presigned_url)
    # find items
    item = df[df["id"] == item_id]
    if item.empty:
        raise Exception(f"Item {item_id} not found in collection {collection_id}")
    return item.to_dict('records')[0] # should use stac-geoparquet to encode geometry correctly
