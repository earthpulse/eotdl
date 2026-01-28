from fastapi import APIRouter, Request, status
from fastapi.exceptions import HTTPException
import logging

from ...src.usecases.auth import generate_login_url
from .responses import login_responses as responses

router = APIRouter()
logger = logging.getLogger(__name__)
_code_store = {}


@router.get("/login", summary='Login to the EOTDL', responses=responses)
def login(request: Request):
    """
    Login to the EOTDL. 
    
    This will return a URL that you can use to authenticate. After authentication, your credentials will be stored locally. 
    It enables future commands to be executed without having to authenticate again (at least while the credentials are valid).
    """
    try:
        redirect_uri = str(request.url_for("callback"))
        response = generate_login_url(redirect_uri)
        state = response.get("state")
        if state:
            _code_store[state] = {
                "code_verifier": response.get("code_verifier"),
                "code": None,
            }
        return response
    except Exception as e:
        logger.exception("login")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
