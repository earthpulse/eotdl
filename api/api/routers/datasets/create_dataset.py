from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends, Body
import logging
from pydantic import BaseModel
from typing import List

from ..auth import get_current_user
from ...src.models import User
from ...src.usecases.datasets import create_dataset
from .responses import create_dataset_responses

router = APIRouter()
logger = logging.getLogger(__name__)


class CreateDatasetBody(BaseModel):
    name: str
    authors: List[str]
    source: str
    license: str
    thumbnail: str
    description: str

@router.post("", summary="Create a new dataset", responses=create_dataset_responses)
def create(
    body: CreateDatasetBody = Body(..., description="Metadata of the dataset (README.md file content)"),
    user: User = Depends(get_current_user),
):
    """
    Create a new dataset. A request body must be provided, and must contain the following fields:
    - name: the name of the dataset.
    - authors: the author or authors of the dataset.
    - license: the license of the dataset.
    - source: the source of the dataset.
    - thumbnail: an image to use as the thumbnail of the dataset in the website.
    """
    try:
        dataset = create_dataset(
            user,
            body.name,
            body.authors,
            body.source,
            body.license,
            body.thumbnail,
            body.description,
        )
        return dataset
    except Exception as e:
        logger.exception("datasets:create")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))