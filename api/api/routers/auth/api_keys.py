from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
import logging

from ...src.usecases.user import retrieve_api_keys, create_api_key, delete_api_key
from ...src.models import User
from .main import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/keys")
def retrieve_user_api_keys(
    user: User = Depends(get_current_user),
):
    try:
        return retrieve_api_keys(user)
    except Exception as e:
        logger.exception("auth.retrieve_user_api_keys")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/keys")
def create_user_api_keys(
    user: User = Depends(get_current_user),
):
    try:
        return create_api_key(user)
    except Exception as e:
        logger.exception("auth.retrieve_user_api_keys")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.delete("/keys/{key}")
def delete_user_api_keys(
    key: str,
    user: User = Depends(get_current_user),
):
    try:
        return delete_api_key(user, key)
    except Exception as e:
        logger.exception("auth.delete_user_api_keys")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
