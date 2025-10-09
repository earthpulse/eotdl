import stac_geoparquet
from fastapi import Request
import requests
import tempfile
import os
import pyarrow.parquet as pq

from ..datasets.retrieve_dataset import retrieve_dataset_by_name
from ..models.retrieve_model import retrieve_model_by_name
from ..pipelines.retrieve_pipeline import retrieve_pipeline_by_name
from ...errors import DatasetDoesNotExistError, ModelDoesNotExistError
from ...repos import OSRepo

def retrieve_stac_item(collection_name: str, item_id: str, version: int = 1, request: Request = None):
    """
    Retrieve a single STAC Item by ID from a collection.
    Returns a properly formatted STAC Item.
    """
    try:
        data = retrieve_dataset_by_name(collection_name)
    except DatasetDoesNotExistError:
        try:
            data = retrieve_model_by_name(collection_name)
        except ModelDoesNotExistError:
            data = retrieve_pipeline_by_name(collection_name)
    
    os_repo = OSRepo()
    catalog_presigned_url = os_repo.get_presigned_url(data.id, f"catalog.v{version}.parquet")
    
    # Download the file first since stac_geoparquet doesn't support HTTP URLs directly
    with tempfile.NamedTemporaryFile(delete=False, suffix='.parquet') as temp_file:
        try:
            # Download the file from the presigned URL
            response = requests.get(catalog_presigned_url)
            response.raise_for_status()
            temp_file.write(response.content)
            temp_file.flush()
            
            # Read the parquet file
            table = pq.read_table(temp_file.name)
            # Use pyarrow to filter the table for the item_id directly, using an array-like boolean mask
            id_column = table.column("id")
            mask = id_column.to_numpy() == item_id
            # pyarrow.Table.filter expects a pyarrow.BooleanArray or numpy array
            filtered_table = table.filter(mask)
            if filtered_table.num_rows > 0:
                # stac_geoparquet expects a table, so we can use stac_table_to_items on the filtered table
                items = list(stac_geoparquet.arrow.stac_table_to_items(filtered_table))
                if items:
                    item = items[0]
                    
                    # Add STAC item links
                    if "links" not in item:
                        item["links"] = []
                    
                    # Add self link
                    item["links"].append({
                        "rel": "self",
                        "type": "application/geo+json",
                        "href": f"/stac/collections/{collection_name}/items/{item_id}"
                    })
                    
                    # Add parent link (collection)
                    item["links"].append({
                        "rel": "parent",
                        "type": "application/json",
                        "href": f"/stac/collections/{collection_name}"
                    })
                    
                    # Add collection link
                    item["links"].append({
                        "rel": "collection",
                        "type": "application/json",
                        "href": f"/stac/collections/{collection_name}"
                    })
                    
                    # Add root link
                    item["links"].append({
                        "rel": "root",
                        "type": "application/json",
                        "href": "/stac"
                    })
                    
                    # Clean up the temporary file
                    if os.path.exists(temp_file.name):
                        os.unlink(temp_file.name)
                    return item
            
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
    raise Exception(f"Item {item_id} not found in collection {collection_name}")