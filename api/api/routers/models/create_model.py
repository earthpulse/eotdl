from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends
import logging
from pydantic import BaseModel
from typing import List

from ..auth import get_current_user
from ...src.models import User
from ...src.usecases.models import create_model, create_model_version

router = APIRouter()
logger = logging.getLogger(__name__)


class CreateModelBody(BaseModel):
    name: str
    authors: List[str]
    source: str
    license: str


@router.post("")
def create(
    metadata: CreateModelBody,
    user: User = Depends(get_current_user),
):
    try:
        model_id = create_model(
            user, metadata.name, metadata.authors, metadata.source, metadata.license
        )
        return {"model_id": model_id}
    except Exception as e:
        logger.exception("models:ingest")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/version/{model_id}")
def version_model(model_id: str, user: User = Depends(get_current_user)):
    try:
        version = create_model_version(user, model_id)
        return {"model_id": model_id, "version": version}
    except Exception as e:
        logger.exception("models:version")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
