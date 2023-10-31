from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends, Query, Path
import logging
from typing import Union

from ..auth import get_current_user
from ...src.models import Dataset
from ...src.usecases.datasets import (
    retrieve_datasets,
    retrieve_dataset_by_name,
    retrieve_dataset_files,
    retrieve_datasets_leaderboard,
    retrieve_popular_datasets,
    # retrieve_liked_datasets,
)
from .responses import retrieve_datasets_responses, retrieve_files_responses

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("", response_model=Dataset, summary="Retrieve list of datasets", responses=retrieve_datasets_responses)
def retrieve(name: str = Query(None, description="Name of the dataset"), 
             match: str = Query(None, description="Match datasets by name"), 
             limit: Union[int, None] = Query(None, description="Limit the number of datasets returned")):
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
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/{dataset_id}/files", summary="Retrieve list of files of a dataset", responses=retrieve_files_responses)
def retrieve_files(
    dataset_id: str = Path(..., description="ID of the dataset"),
    version: int = Query(None, description="Version of the dataset"),
):
    """
    Retrieve a list with the files of a given dataset. Files can be optionally filtered by version.
    """
    try:
        return retrieve_dataset_files(dataset_id, version)
    except Exception as e:
        logger.exception("datasets:retrieve")
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


# @router.get("/liked", include_in_schema=False)
# def retrieve_liked(
#     user: User = Depends(get_current_user),
# ):
#     try:
#         return retrieve_liked_datasets(user)
#     except Exception as e:
#         logger.exception("datasets:retrieve_liked")
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
