import pandas as pd
import stac_geoparquet
from fastapi import Request
import json
from typing import Optional

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
    
    # Use stac_geoparquet to read the catalog
    try:
        # Try to use stac_geoparquet for better STAC handling
        catalog = stac_geoparquet.read_geoparquet(catalog_presigned_url)
        df = catalog
    except Exception:
        # Fallback to pandas if stac_geoparquet fails
        df = pd.read_parquet(catalog_presigned_url)
    
    # Find the specific item
    item_row = df[df["id"] == item_id]
    if item_row.empty:
        raise Exception(f"Item {item_id} not found in collection {collection_name}")
    
    # Get the item data
    item_data = item_row.to_dict('records')[0]
    
    # Parse geometry if it's a string
    geometry = item_data.get("geometry", {})
    if isinstance(geometry, str):
        try:
            geometry = json.loads(geometry)
        except json.JSONDecodeError:
            geometry = {}
    
    # Parse assets if it's a string
    assets = item_data.get("assets", {})
    if isinstance(assets, str):
        try:
            assets = json.loads(assets)
        except json.JSONDecodeError:
            assets = {}
    
    # Build the STAC Item
    item = {
        "stac_version": "1.0.0",
        "type": "Feature",
        "id": str(item_data.get("id", "")),
        "geometry": geometry,
        "properties": {
            "datetime": item_data.get("datetime", ""),
            "start_datetime": item_data.get("start_datetime", ""),
            "end_datetime": item_data.get("end_datetime", ""),
        },
        "assets": assets,
        "links": [
            {
                "rel": "self",
                "href": f"{request.base_url}stac/collections/{collection_name}/items/{item_id}" if request else f"/stac/collections/{collection_name}/items/{item_id}",
                "type": "application/geo+json"
            },
            {
                "rel": "parent",
                "href": f"{request.base_url}stac/collections/{collection_name}" if request else f"/stac/collections/{collection_name}",
                "type": "application/json"
            },
            {
                "rel": "collection",
                "href": f"{request.base_url}stac/collections/{collection_name}" if request else f"/stac/collections/{collection_name}",
                "type": "application/json"
            }
        ]
    }
    
    # Add any additional properties from the item data
    for key, value in item_data.items():
        if key not in ["id", "geometry", "datetime", "start_datetime", "end_datetime", "assets"]:
            if value is not None and value != "":  # Only add non-null values
                item["properties"][key] = value
    
    return item
