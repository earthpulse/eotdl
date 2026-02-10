from fastapi import APIRouter, status, HTTPException
import logging

from ...src.usecases.auth import update_auth_state


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/callback", name="callback", include_in_schema=False)
def callback(code: str = None, state: str = None):
    try:
        update_auth_state(state, code)
        return "Login successful! You may now close this window."
    except Exception as e:
        logger.exception("callback")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
