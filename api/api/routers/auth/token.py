from fastapi import APIRouter, status, Query
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
import logging

from ...src.usecases.auth import generate_id_token
from .responses import token_responses as responses

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/token", summary='Get EOTDL ID token', responses=responses)
def token(code: str = Query(None, description="The code that you received after logging in.")):
    """
    Generate an ID token for the current EOTDL user.
    """
    try:
        return generate_id_token(code)
    except Exception as e:
        logger.exception("token")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
