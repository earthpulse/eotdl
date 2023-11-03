from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
import logging

from ...src.usecases.user import retrieve_user_credentials
from ...src.models import User
from .main import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/credentials", include_in_schema=False)
def retrieve_credentials(
    user: User = Depends(get_current_user),
):
    try:
        return retrieve_user_credentials(user)
    except Exception as e:
        logger.exception("auth.retrieve_credentials")
        print(e)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
