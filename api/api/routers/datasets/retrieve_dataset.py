import traceback
from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends, Query, Path
import logging
from typing import Union

from ..auth import get_current_user
from ...src.models import User
from ...src.usecases.datasets import (
    retrieve_datasets,
    retrieve_dataset_by_name,
    retrieve_private_dataset_by_name,
    retrieve_datasets_leaderboard,
    retrieve_popular_datasets,
    retrieve_private_datasets
)
from .responses import retrieve_datasets_responses, retrieve_files_responses

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "", summary="Retrieve list of datasets", responses=retrieve_datasets_responses
)
def retrieve(
    name: str = Query(None, description="Name of the dataset"),
    match: str = Query(None, description="Match datasets by name"),
    limit: Union[int, None] = Query(
        None, description="Limit the number of datasets returned"
    ),
):
    """
    Retrieve a list of the datasets in the EOTDL, with dataset information such as name, license and authors.
    Datasets can be optionally filtered by name and limited by number.
    """
    try:
        if name is None:
            return retrieve_datasets(match, limit)
        return retrieve_dataset_by_name(name)
    except Exception as e:
        logger.exception("datasets:retrieve")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.get(
    "/private", summary="Retrieve list of private datasets"
)
def retrieve_private(
    name: str = Query(None, description="Name of the dataset"),
    user: User = Depends(get_current_user),
):
    try:
        if name is None:
            return retrieve_private_datasets(user)
        return retrieve_private_dataset_by_name(name, user)
    except Exception as e:
        logger.exception("datasets:retrieve")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/leaderboard", include_in_schema=False)
def leaderboard():
    try:
        return retrieve_datasets_leaderboard()
    except Exception as e:
        logger.exception("datasets:leaderboard")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.get("/popular", include_in_schema=False)
def retrieve_popular(limit: Union[int, None] = None):
    try:
        return retrieve_popular_datasets(limit)
    except Exception as e:
        logger.exception("datasets:retrieve_popular")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
