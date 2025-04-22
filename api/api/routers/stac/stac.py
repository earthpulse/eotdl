from fastapi import APIRouter, HTTPException, status
import logging
import traceback
from pydantic import BaseModel
from typing import Optional
from ...src.usecases.stac import retrieve_stac_collections, retrieve_stac_collection, retrieve_stac_items, search_stac_columns, retrieve_stac_item, search_stac_items

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("")
def stac():
    return {"message": "Welcome to the STAC API"}
    
@router.get("/collections")
def collections():
    try:
        return retrieve_stac_collections()
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