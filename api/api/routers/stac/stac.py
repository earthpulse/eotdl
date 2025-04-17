from fastapi import APIRouter, HTTPException, status
import logging
import traceback
from pydantic import BaseModel
from typing import Optional
from ...src.usecases.stac import retrieve_stac_collections, retrieve_stac_collection, retrieve_stac_items, search_stac_columns, retrieve_stac_item, search_stac_items

router = APIRouter()
logger = logging.getLogger(__name__)


# here the core conformance class needs to be implemented
@router.get("")
def stac():

    core_response = {
        "stac_version": "1.0.0",
        "id": "eotdl-stac-api",
        "title": "EOTDL STAC API",
        "description": "EOTDSL STAC API Landing Page",
        "type": "Catalog",
        "conformsTo": [
            "https://api.stacspec.org/v1.0.0/core",
            # "https://api.stacspec.org/v1.0.0/item-search"
            # "https://api.stacspec.org/v1.0.0/collections"
        ],
        "links": [
            {
            "rel": "self",
            "type": "application/json",
            "href": "https://stac-api.example.com"
            },
            {
            "rel": "root",
            "type": "application/json",
            "href": "https://stac-api.example.com"
            },
        #     {
        #     "rel": "search",
        #     "type": "application/json",
        #     "href": "https://my.api.com/search"
        #     },
        #     {
        #     "rel": "collections",
        #     "type": "application/json",
        #     "href": "https://my.api.com/collections"
        #     }
        ]
        }


    return core_response

# there also needs to be a "/api" that returns a description of the service
@router.get("/api")
def api():
    return "Endpoint include collections and search"
    
@router.get("/collections")
def collections():
    try:
        return retrieve_stac_collections()
    except Exception as e:
        logger.exception("stac:collections")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.get("/collections/{collection_id}")
def collection(collection_id: str):
    try:
        return retrieve_stac_collection(collection_id)
    except Exception as e:
        logger.exception("stac:collection")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    
@router.get("/collections/{collection_id}/items")
def items(collection_id: str, version: Optional[int] = 1):
    try:
        return retrieve_stac_items(collection_id, version)
    except Exception as e:
        logger.exception("stac:items")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    
@router.get("/collections/{collection_id}/items/{item_id}")
def item(collection_id: str, item_id: str, version: Optional[int] = 1):
    try:
        return retrieve_stac_item(collection_id, item_id, version)
    except Exception as e:
        logger.exception("stac:item")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    
@router.get("/search")
def search(collection_id: str):
    try:
        return search_stac_columns(collection_id)
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