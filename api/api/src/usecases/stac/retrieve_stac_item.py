import pandas as pd

from ..datasets import retrieve_dataset_by_name
from ...repos import OSRepo

# TODO: versioning

def retrieve_stac_item(collection_id, item_id):
    dataset = retrieve_dataset_by_name(collection_id)
    os_repo = OSRepo()
    catalog_presigned_url = os_repo.get_presigned_url(dataset.id, "catalog.v1.parquet")
    # this read the entire catalog into memory, which is not ideal
    df = pd.read_parquet(catalog_presigned_url)
    # find items
    item = df[df["id"] == item_id]
    if item.empty:
        raise Exception(f"Item {item_id} not found in collection {collection_id}")
    return item.to_dict('records')[0] # should use stac-geoparquet to encode geometry correctly
