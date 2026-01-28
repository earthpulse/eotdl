from fastapi import APIRouter, status, Query, Request
from fastapi.exceptions import HTTPException
import logging

from ...src.usecases.auth import exchange_code_for_tokens
from .login import _code_store
from .responses import token_responses as responses

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/token", summary='Get EOTDL ID token', responses=responses)
def token(
    request: Request,
    state: str = Query(None, description="The state that you received after logging in."),
):
    """
    Generate an ID token for the current EOTDL user.
    """
    try:
        data = _code_store.get(state)
        if not data or not data.get("code") or not data.get("code_verifier"):
            raise HTTPException(status_code=400, detail="Code or code_verifier not found")
        tokens = exchange_code_for_tokens(
            code=data["code"],
            code_verifier=data["code_verifier"],
            redirect_uri=str(request.url_for("callback")),
        )
        _code_store.pop(state)
        return tokens
    except Exception as e:
        logger.exception("token")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
