import pandas as pd
import stac_geoparquet
import pyarrow.parquet as pq
from tqdm import tqdm
import requests
import tempfile
import os

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
    
    # Download the file first since pyarrow doesn't support HTTP URLs directly
    with tempfile.NamedTemporaryFile(delete=False, suffix='.parquet') as temp_file:
        try:
            # Download the file from the presigned URL
            response = requests.get(catalog_presigned_url)
            response.raise_for_status()
            temp_file.write(response.content)
            temp_file.flush()
            
            # Read the parquet file
            table = pq.read_table(temp_file.name)
            items = []
            for item in tqdm(stac_geoparquet.arrow.stac_table_to_items(table), total=len(table)):
                items.append(item)
            
            # Return as FeatureCollection according to STAC API specification
            return {
                "type": "FeatureCollection",
                "features": items,
                "links": [
                    {
                        "rel": "self",
                        "type": "application/geo+json",
                        "href": f"/stac/collections/{collection_name}/items"
                    },
                    {
                        "rel": "parent",
                        "type": "application/json",
                        "href": f"/stac/collections/{collection_name}"
                    },
                    {
                        "rel": "root",
                        "type": "application/json",
                        "href": "/stac"
                    }
                ],
                "numberMatched": len(items),
                "numberReturned": len(items)
            }
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)