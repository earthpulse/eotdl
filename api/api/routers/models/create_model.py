from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends, Body
import logging
from pydantic import BaseModel
from typing import List

from ..auth import get_current_user
from ...src.models import User
from ...src.usecases.models import create_model
from .responses import create_model_responses

router = APIRouter()
logger = logging.getLogger(__name__)


class CreateModelBody(BaseModel):
    name: str
    authors: List[str]
    source: str
    license: str
    thumbnail: str
    description: str


@router.post("", summary="Create a new model", responses=create_model_responses)
def create(
    metadata: CreateModelBody = Body(..., description="Metadata of the model"),
    user: User = Depends(get_current_user),
):
    """
    Create a new model. A request body must be provided, and must contain the following fields:
    - name: the name of the model.
    - authors: the author or authors of the model.
    - license: the license of the model.
    - source: the source of the model.
    """
    try:
        model = create_model(
            user, metadata.name, metadata.authors, metadata.source, metadata.license, metadata.thumbnail, metadata.description
        )
        return model
    except Exception as e:
        logger.exception("models:ingest")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
