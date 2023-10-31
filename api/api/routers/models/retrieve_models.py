from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status
import logging
from typing import Union

# from ..auth import get_current_user
# from ...src.models import User
from ...src.usecases.models import (
    retrieve_models,
    retrieve_model_by_name,
    retrieve_models_leaderboard,
    retrieve_model_files,
    retrieve_popular_models,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("")
def retrieve(name: str = None, match: str = None, limit: Union[int, None] = None):
    try:
        if name is None:
            return retrieve_models(match, limit)
        return retrieve_model_by_name(name)
    except Exception as e:
        logger.exception("models:retrieve")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/leaderboard", include_in_schema=False)
def leaderboard():
    try:
        return retrieve_models_leaderboard()
    except Exception as e:
        logger.exception("models:leaderboard")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/{model_id}/files")
def retrieve_files(
    model_id: str,
    version: int = None,
):
    try:
        return retrieve_model_files(model_id, version)
    except Exception as e:
        logger.exception("models:retrieve")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/popular", include_in_schema=False)
def retrieve_popular(limit: Union[int, None] = None):
    try:
        return retrieve_popular_models(limit)
    except Exception as e:
        logger.exception("models:retrieve_popular")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
