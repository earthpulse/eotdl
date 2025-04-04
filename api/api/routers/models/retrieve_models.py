from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Query, Path
import logging
from typing import Union

from ...src.usecases.models import (
    retrieve_models,
    retrieve_model_by_name,
    retrieve_models_leaderboard,
    retrieve_popular_models,
)
from .responses import retrieve_models_responses, retrieve_files_responses

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("", summary="Retrieve list of models", responses=retrieve_models_responses)
def retrieve(
    name: str = Query(None, description="Name of the model"),
    match: str = Query(None, description="Match models by name"),
    limit: Union[int, None] = Query(
        None, description="Limit the number of models returned"
    ),
):
    """
    Retrieve a list of the models in the EOTDL, with model information such as name, license and authors.
    Models can be optionally filtered by name and limited by number.
    """
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

@router.get("/popular", include_in_schema=False)
def retrieve_popular(limit: Union[int, None] = None):
    try:
        return retrieve_popular_models(limit)
    except Exception as e:
        logger.exception("models:retrieve_popular")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
