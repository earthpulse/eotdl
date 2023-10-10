from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends
import logging
from typing import Optional, List
from pydantic import BaseModel

from ..auth import get_current_user
from ...src.models import User
from ...src.usecases.datasets import toggle_like_dataset, update_dataset

router = APIRouter()
logger = logging.getLogger(__name__)


@router.put("/{id}/like", include_in_schema=False)
def like(
    id: str,
    user: User = Depends(get_current_user),
):
    try:
        return toggle_like_dataset(id, user)
    except Exception as e:
        logger.exception("datasets:like")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


class UpdateBody(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    authors: Optional[List[str]] = None
    source: Optional[str] = None
    license: Optional[str] = None


@router.put("/{dataset_id}")
def update(
    dataset_id: str,
    body: UpdateBody,
    user: User = Depends(get_current_user),
):
    try:
        return update_dataset(
            dataset_id,
            user,
            body.name,
            body.authors,
            body.source,
            body.license,
            body.tags,
            body.description,
        )
    except Exception as e:
        logger.exception("datasets:ingest")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
