from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends, Path, Body
import logging
from pydantic import BaseModel
from typing import Optional, List
import traceback

from ..auth import get_current_user
from ...src.models import User, Pipeline
from ...src.usecases.pipelines import update_pipeline, toggle_like_pipeline, deactivate_pipeline

router = APIRouter()
logger = logging.getLogger(__name__)


@router.put("/{id}/like", include_in_schema=False)
def like(
    id: str,
    user: User = Depends(get_current_user),
):
    try:
        return toggle_like_pipeline(id, user)
    except Exception as e:
        logger.exception("pipelines:like")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


class UpdateBody(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    authors: Optional[List[str]] = None
    source: Optional[str] = None
    license: Optional[str] = None
    thumbnail: Optional[str] = None


@router.put(
    "/{pipeline_id}", summary="Update a pipeline"
)
def update(
    pipeline_id: str = Path(..., description="ID of the pipeline"),
    body: Pipeline = Body(..., description="Metadata of the pipeline"),
    user: User = Depends(get_current_user),
):
    """
    Update a pipeline.
    """
    try:
        return update_pipeline(
            pipeline_id,
            user,
            body,
        )
    except Exception as e:  
        print(traceback.format_exc())
        logger.exception("pipelines:update")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.patch("/deactivate/{pipeline_id}", include_in_schema=False)
def deactivate(
    pipeline_id: str,
    user: User = Depends(get_current_user),
):
    try:
        message = deactivate_pipeline(pipeline_id, user)
        return {"message": message}
    except Exception as e:
        logger.exception("pipelines:deactivate")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
