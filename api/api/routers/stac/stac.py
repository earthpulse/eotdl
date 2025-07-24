import logging
import traceback

from fastapi import APIRouter, HTTPException, status, Request
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional


from ...src.usecases.stac import retrieve_stac_collections, retrieve_stac_collection, retrieve_stac_items, search_stac_columns, retrieve_stac_item, search_stac_items
from ...config import VERSION

router = APIRouter()
logger = logging.getLogger(__name__)

conforms_to = [
    "https://api.stacspec.org/v1.0.0/core"
]


@router.get("")
def stac_landing_page(request: Request):
    base_url = str(request.base_url)
    core_response = {
        "stac_version": VERSION,
        "id": "eotdl-stac-api",
        "title": "EOTDL STAC API",
        "description": "EOTDSL STAC API Landing Page",
        "type": "Catalog",
        "conformsTo": conforms_to,
        "links": [
            {
                "rel": "self",
                "type": "application/json",
                "href": base_url + "stac"
            },
            {
                "rel": "root",
                "type": "application/json",
                "href": base_url + "stac"
            },
            {
                "rel": "conformance",
                "type": "application/json",
                "href": base_url + "stac/conformance"
            },
            {
                "rel": "service-desc",
                "type": "application/vnd.oai.openapi+json;version=3.0",
                "href": base_url + "stac/api"
            },
            {
                "rel": "service-doc",
                "type": "text/html",
                "href": base_url + "stac/api.html"
            },
            {
                "rel": "search",
                "type": "application/json",
                "href": base_url + "stac/search",
                "method": "GET"
            },
            {
                "rel": "search",
                "type": "application/geo+json",
                "href": base_url + "stac/search",
                "method": "POST"
            },
            {
                "rel": "collections",
                "type": "application/json",
                "href": base_url + "stac/collections"
            }
        ]
        }

    return core_response

@router.get("/conformance")
def conformance():
    return {
        "conformsTo": conforms_to
    }

@router.get("/api", include_in_schema=False)
def api(request: Request):
    openapi_schema = get_openapi(
        title="EOTDL STAC API",
        version=VERSION,
        routes=request.app.routes,
        description="STAC-compliant OpenAPI schema"
    )
    return JSONResponse(content=openapi_schema, media_type="application/vnd.oai.openapi+json;version=3.0")

@router.get("/api.html", include_in_schema=False)
def api_html(request: Request):
    return get_swagger_ui_html(
        openapi_url=str(request.base_url) + "stac/api",
        title="EOTDL STAC API"
    )

@router.get("/collections")
def collections(request: Request):
    try:
        return retrieve_stac_collections(request)
    except Exception as e:
        logger.exception("stac:collections")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.get("/collections/{collection_name}")
def collection(collection_name: str):
    try:
        return retrieve_stac_collection(collection_name)
    except Exception as e:
        logger.exception("stac:collection")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    
@router.get("/collections/{collection_nam}/items")
def items(collection_nam: str, version: Optional[int] = 1):
    try:
        return retrieve_stac_items(collection_nam, version)
    except Exception as e:
        logger.exception("stac:items")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    
@router.get("/collections/{collection_name}/items/{item_id}")
def item(collection_name: str, item_id: str, version: Optional[int] = 1):
    try:
        return retrieve_stac_item(collection_name, item_id, version)
    except Exception as e:
        logger.exception("stac:item")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    
@router.get("/search")
def search(collection: str):
    try:
        return search_stac_columns(collection)
    except Exception as e:
        logger.exception("stac:item")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

class SearchRequest(BaseModel): 
    collection_id: str
    query: str

@router.post("/search")
def search(search_request: SearchRequest):
    try:
        return search_stac_items(search_request.collection_id, search_request.query)
    except Exception as e:
        logger.exception("stac:item")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
