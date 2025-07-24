import pandas as pd

from api.config import VERSION

from ..datasets.retrieve_dataset import retrieve_dataset_by_name
from ..models.retrieve_model import retrieve_model_by_name
from ..pipelines.retrieve_pipeline import retrieve_pipeline_by_name
from ...repos import OSRepo
from ...errors import DatasetDoesNotExistError, ModelDoesNotExistError

def retrieve_stac_items(collection_name, version):
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
    
    features = []
    for _, row in df.iterrows():
        feature = {
            "type": "Feature",
            "stac_version": VERSION,
            "stac_extensions": [],
            "id": row["id"],
            "bbox": row.get("bbox", []),
            "geometry": row.get("geometry", {}),
            "properties": row.get("properties", {}),
            "collection": collection_name,
            "links": [],
            "assets": row.get("assets", {})
        }
        features.append(feature)

    return {
        "type": "FeatureCollection",
        "features": features
    }