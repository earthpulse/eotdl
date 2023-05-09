from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status
import logging

from ..src.usecases.tags import retrieve_tags

logger=logging.getLogger(__name__)

router = APIRouter(
    prefix="/tags",
    tags=["tags"]
)

@router.get("")
def retrieve():
    try:
        return retrieve_tags()
    except Exception as e:
        logger.exception('tags.retrieve')
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))