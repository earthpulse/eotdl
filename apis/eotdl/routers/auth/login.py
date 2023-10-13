from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException
import logging

from ...src.usecases.auth import generate_login_url

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/login")
def login():
    try:
        return generate_login_url()
    except Exception as e:
        logger.exception("login")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

