from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
import logging

from ...src.models import User
from ...src.usecases.auth import generate_id_token
from ...src.usecases.user import retrieve_user
from .main import get_current_user
from .responses import me_responses as responses

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/me", response_model=User, summary='Get EOTDL user', responses=responses)
def me(user: User = Depends(get_current_user)):
    """
    Get the current EOTDL user's information.
    """
    try:
        return retrieve_user(user.uid)
    except Exception as e:
        logger.exception("me")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
