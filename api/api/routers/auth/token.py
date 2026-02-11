from fastapi import APIRouter, status, Query, Request
from fastapi.exceptions import HTTPException
import logging
import traceback

from ...src.usecases.auth import exchange_code_for_tokens
from .responses import token_responses as responses

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/token", summary="Get EOTDL ID token", responses=responses)
def token(
    request: Request,
    state: str = Query(
        None, description="The state that you received after logging in."
    ),
):
    """
    Generate an ID token for the current EOTDL user.
    """
    try:
        redirect_uri = str(request.url_for("callback"))
        return exchange_code_for_tokens(state, redirect_uri)
    except Exception as e:
        traceback.print_exc()
        logger.exception("token")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
