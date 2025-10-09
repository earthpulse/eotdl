from fastapi import Request

from api.config import VERSION

from ..datasets import retrieve_datasets
from ..models import retrieve_models
from ..pipelines import retrieve_pipelines


def retrieve_stac_collections(request: Request):
    datasets = retrieve_datasets()
    models = retrieve_models()
    pipelines = retrieve_pipelines()

    # Handle HTTPS in production behind reverse proxy
    if request.headers.get("x-forwarded-proto") == "https":
        base_url = str(request.base_url).replace("http://", "https://").rstrip("/") + "/stac/collections"
    else:
        base_url = str(request.base_url).rstrip("/") + "/stac/collections"
    collections = []
    links = []

    def build_collection(obj):
        return {
            "stac_version": "1.0.0",
            "type": "Collection",
            # "id": obj.id,
            "id": obj.name, # if we use id the items will not be found
            "title": obj.name,
            "description": f"{obj.name} collection",
            "license": "proprietary",
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
                }
            ]
        }

    for obj in datasets + models + pipelines:
        collections.append(build_collection(obj))
        links.append({
            "href": f"{base_url}/{obj.name}",
            "rel": "child",
            "type": "application/json",
            "title": obj.name
        })

    # Add self link to the root response
    links.append({
        "href": base_url,
        "rel": "self",
        "type": "application/json"
    })

    return {
        "collections": collections,
        "links": links
    }