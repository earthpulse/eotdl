from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
import logging

from ...src.usecases.auth import generate_login_url
from .responses import login_responses as responses

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/login", summary='Login to the EOTDL', responses=responses)
def login():
    """
    Login to the EOTDL. 
    
    This will return a URL that you can use to authenticate. After authentication, your credentials will be stored locally. 
    It enables future commands to be executed without having to authenticate again (at least while the credentials are valid).
    """
    try:
        return generate_login_url()
    except Exception as e:
        logger.exception("login")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

