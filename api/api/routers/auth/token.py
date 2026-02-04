from fastapi import APIRouter, status, Query, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
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
        if not state:
            raise HTTPException(status_code=400, detail="Invalid login state")
        redirect_uri = str(request.url_for("callback"))
        try:
            return exchange_code_for_tokens(state, redirect_uri)
        except Exception as e:
            if str(e) == "Code not found":
                return JSONResponse(
                    status_code=status.HTTP_202_ACCEPTED,
                    content={"detail": "Authorization pending"},
                )
            if str(e) == "Auth state not found":
                raise HTTPException(status_code=400, detail="Invalid login state")
            raise
    except Exception as e:
        traceback.print_exc()
        logger.exception("token")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
