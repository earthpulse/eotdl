from fastapi import Request

from api.config import VERSION

from ..datasets import retrieve_datasets
from ..models import retrieve_models
from ..pipelines import retrieve_pipelines


def retrieve_stac_collections(request: Request):
    datasets = retrieve_datasets()
    models = retrieve_models()
    pipelines = retrieve_pipelines()

    base_url = str(request.base_url).rstrip("/") + "/stac/collections"
    collections = []
    links = []

    def build_collection(obj):
        return {
            "stac_version": VERSION,
            "type": "Collection",
            "id": obj.id,
            "title": obj.name,
            "description": f"{obj.name} collection",
            "license": "proprietary",
            "extent": {
                "spatial": {
                    "bbox": [obj.metadata.spatial_bbox]
                },
                "temporal": {
                    "interval": [obj.metadata.temporal_interval]
                }
            },
            "links": [
                {
                    "href": f"{base_url}/{obj.id}/items",
                    "rel": "items",
                    "type": "application/geo+json"
                }
            ]
        }

    def build_link(obj):
        return {
            "href": f"{base_url}/{obj.id}",
            "rel": "collection",
            "type": "application/json",
            "title": obj.name,
            "method": "GET"
        }

    for obj in datasets + models + pipelines:
        collections.append(build_collection(obj))
        links.append(build_link(obj))

    return {
        "links": links,
        "collections": collections
    }
