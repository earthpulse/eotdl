import pandas as pd

from ..datasets import retrieve_dataset_by_name
from ...repos import OSRepo

# TODO: versioning

def retrieve_stac_items(collection_id):
    dataset = retrieve_dataset_by_name(collection_id)
    os_repo = OSRepo()
    catalog_presigned_url = os_repo.get_presigned_url(dataset.id, "catalog.v1.parquet")
    # this read the entire catalog into memory, which is not ideal
    df = pd.read_parquet(catalog_presigned_url)
    item_ids = df["id"].tolist()
    # should format items in some particular way???
    return item_ids