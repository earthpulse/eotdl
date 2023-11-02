from fastapi import APIRouter, status, Request, Query
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
import logging

from ...src.usecases.auth import generate_logout_url
from .responses import logout_responses as responses

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/callback", name="callback", include_in_schema=False)
def logout_callback():
    return "You are logged out."


@router.get("/logout", summary='Logout from the EOTDL', responses=responses)
def logout(request: Request, redirect_uri: str = Query(None, description="The URL to redirect to after logging out.")):
    """
    Logout from the EOTDL. 
    
    This will return a logout url that you can visit in case you want to authenticate with a different account.
    """
    try:
        if redirect_uri is None:
            redirect_uri = str(request.url_for("callback"))
        logout_url = generate_logout_url(redirect_uri)
        return {"logout_url": logout_url}
    except Exception as e:
        logger.exception("logout")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
