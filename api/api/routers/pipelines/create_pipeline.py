from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends, Body
import logging
from pydantic import BaseModel
from typing import List
import traceback

from ..auth import get_current_user
from ...src.models import User
from ...src.usecases.pipelines import create_pipeline

router = APIRouter()
logger = logging.getLogger(__name__)


class CreatePipelineBody(BaseModel):
    name: str
    authors: List[str]
    source: str
    license: str
    thumbnail: str
    description: str


@router.post("", summary="Create a new pipeline")
def create(
    metadata: CreatePipelineBody = Body(..., description="Metadata of the pipeline"),
    user: User = Depends(get_current_user),
):
    try:
        pipeline = create_pipeline(
            user, metadata.name, metadata.authors, metadata.source, metadata.license, metadata.thumbnail, metadata.description
        )
        return pipeline
    except Exception as e:
        logger.exception("pipelines:ingest")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
