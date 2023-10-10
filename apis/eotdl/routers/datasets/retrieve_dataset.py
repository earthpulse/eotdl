from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends
import logging
from typing import Union

from ..auth import get_current_user
from ...src.models import User
from ...src.usecases.datasets import (
    retrieve_datasets,
    retrieve_dataset_by_name,
    # retrieve_datasets_leaderboard,
    # retrieve_liked_datasets,
    # retrieve_popular_datasets,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("")
def retrieve(name: str = None, match: str = None, limit: Union[int, None] = None):
    try:
        if name is None:
            return retrieve_datasets(match, limit)
        return retrieve_dataset_by_name(name)
    except Exception as e:
        logger.exception("datasets:retrieve")
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


# @router.get("/popular", include_in_schema=False)
# def retrieve_popular(limit: Union[int, None] = None):
#     try:
#         return retrieve_popular_datasets(limit)
#     except Exception as e:
#         logger.exception("datasets:retrieve_popular")
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

# @router.get("/leaderboard", include_in_schema=False)
# def leaderboard():
#     try:
#         return retrieve_datasets_leaderboard()
#     except Exception as e:
#         logger.exception("datasets:leaderboard")
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
