from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status
import logging

from ...src.usecases.tags import retrieve_tags, retrieve_tags_with_categories

logger = logging.getLogger(__name__)
router = APIRouter()

responses = {
    200: {
        "content": {
            "application/json": {
                "example": [
                    "agriculture",
                    "image classification",
                    "land cover",
                    "object detection",
                    "segmentation",
                    "sentinel-1",
                    "sentinel-2",
                ]
            }
        }
    }
}


@router.get("", summary="Retrieve tags", responses=responses)
def retrieve():
    """
    Retrieve all datasets and models tags in the EOTDL.
    """
    try:
        return retrieve_tags()
    except Exception as e:
        logger.exception("tags.retrieve")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/categories", summary="Retrieve tags with categories", responses=responses)
def retrieve_tags_and_categories():
    """
    Retrieve all datasets and models tags in the EOTDL (with categories).
    """
    try:
        return retrieve_tags_with_categories()
    except Exception as e:
        logger.exception("tags.retrieve_tags_with_categories")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
