from fastapi import APIRouter, status, Request
from fastapi.exceptions import HTTPException
import logging

from ...src.usecases.auth import generate_logout_url

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/callback", name="callback", include_in_schema=False)
def logout_callback():
    return "You are logged out."


@router.get("/logout")
def logout(request: Request, redirect_uri: str = None):
    try:
        if redirect_uri is None:
            redirect_uri = str(request.url_for("callback"))
        logout_url = generate_logout_url(redirect_uri)
        return {"logout_url": logout_url}
    except Exception as e:
        logger.exception("logout")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
