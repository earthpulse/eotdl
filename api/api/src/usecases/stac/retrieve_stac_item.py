import pandas as pd

from ..datasets.retrieve_dataset import retrieve_dataset_by_name
from ..models.retrieve_model import retrieve_model_by_name
from ..pipelines.retrieve_pipeline import retrieve_pipeline_by_name
from ...errors import DatasetDoesNotExistError, ModelDoesNotExistError
from ...repos import OSRepo

# TODO: versioning

def retrieve_stac_item(collection_name, item_id, version):
    try:
        data = retrieve_dataset_by_name(collection_name)
    except DatasetDoesNotExistError:
        try:
            data = retrieve_model_by_name(collection_name)
        except ModelDoesNotExistError:
            data = retrieve_pipeline_by_name(collection_name)
    os_repo = OSRepo()
    catalog_presigned_url = os_repo.get_presigned_url(data.id, f"catalog.v{version}.parquet")
    # this read the entire catalog into memory, which is not ideal
    df = pd.read_parquet(catalog_presigned_url)
    # find items
    item_df = df[df["id"] == item_id]
    if item_df.empty:
        raise Exception(f"Item {item_id} not found in collection {collection_name}")
    
    row = item_df.iloc[0]

    return {
        "type": "Feature",
        "stac_version": "1.0.0",
        "stac_extensions": [],
        "id": row["id"],
        "bbox": row.get("bbox", []),
        "geometry": row.get("geometry", {}),
        "properties": row.get("properties", {}),
        "collection": collection_name,
        "links": [],
        "assets": row.get("assets", {})
    }
