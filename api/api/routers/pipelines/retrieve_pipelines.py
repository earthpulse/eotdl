from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Query, Path
import logging
from typing import Union
import traceback

from ...src.usecases.pipelines import (
    retrieve_pipelines,
    retrieve_pipeline_by_name,
    retrieve_pipelines_leaderboard,
    retrieve_popular_pipelines,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("", summary="Retrieve list of pipelines")
def retrieve(
    name: str = Query(None, description="Name of the pipeline"),
    match: str = Query(None, description="Match pipelines by name"),
    limit: Union[int, None] = Query(
        None, description="Limit the number of pipelines returned"
    ),
):
    try:
        if name is None:
            return retrieve_pipelines(match, limit)
        return retrieve_pipeline_by_name(name)
    except Exception as e:
        logger.exception("pipelines:retrieve")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/leaderboard", include_in_schema=False)
def leaderboard():
    try:
        return retrieve_pipelines_leaderboard()
    except Exception as e:
        logger.exception("pipelines:leaderboard")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.get("/popular", include_in_schema=False)
def retrieve_popular(limit: Union[int, None] = None):
    try:
        return retrieve_popular_pipelines(limit)
    except Exception as e:
        logger.exception("pipelines:retrieve_popular")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
