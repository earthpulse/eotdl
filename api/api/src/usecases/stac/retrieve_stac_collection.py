from fastapi import Request
from ..datasets.retrieve_dataset import retrieve_dataset_by_name
from ..models.retrieve_model import retrieve_model_by_name
from ..pipelines.retrieve_pipeline import retrieve_pipeline_by_name
from ...errors import DatasetDoesNotExistError, ModelDoesNotExistError

def retrieve_stac_collection(collection_name: str, request: Request = None):
    try:
        obj = retrieve_dataset_by_name(collection_name)
    except DatasetDoesNotExistError:
        try:
            obj = retrieve_model_by_name(collection_name)
        except ModelDoesNotExistError:
            obj = retrieve_pipeline_by_name(collection_name)
    
    # Handle HTTPS in production behind reverse proxy
    if request.headers.get("x-forwarded-proto") == "https":
        base_url = str(request.base_url).replace("http://", "https://").rstrip("/") + "/stac/collections"
    else:
        base_url = str(request.base_url).rstrip("/") + "/stac/collections"
    collection = {
        "stac_version": "1.0.0",
        "type": "Collection",
        # "id": obj.id,
        "id": obj.name, # if we use id the items will not be found
        "title": obj.name,
        "description": obj.metadata.description,
        "license": obj.metadata.license,
        # "extent": {
        #     "spatial": {
        #         "bbox": [[-180, -90, 180, 90]]
        #     },
        #     "temporal": {
        #         "interval": [["2020-01-01T00:00:00Z", None]]
        #     }
        # },
        "links": [
            {
                "href": f"{base_url}/{obj.name}",
                "rel": "self",
                "type": "application/json"
            },
            {
                "href": f"{base_url}/{obj.name}/items",
                "rel": "items",
                "type": "application/geo+json"
            },
            {
                "href": base_url,
                "rel": "parent",
                "type": "application/json"
            }
        ]
    }
    
    # # Add collection-specific metadata
    # if hasattr(obj, 'metadata') and obj.metadata:
    #     if hasattr(obj.metadata, 'description') and obj.metadata.description:
    #         collection["description"] = obj.metadata.description
    #     if hasattr(obj.metadata, 'license') and obj.metadata.license:
    #         collection["license"] = obj.metadata.license
    
    # # Add keywords/tags if available
    # if hasattr(obj, 'tags') and obj.tags:
    #     collection["keywords"] = obj.tags
    
    # # Add version information if available
    # if hasattr(obj, 'versions') and obj.versions:
    #     collection["version"] = str(obj.versions[0].version_id) if obj.versions else "1"
    
    return collection