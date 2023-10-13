from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
import logging

from ...src.usecases.user import accept_user_terms_and_conditions
from ...src.models import User
from .main import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/accept", include_in_schema=False)
def accept_terms_and_contitions(
    user: User = Depends(get_current_user),
):
    try:
        return accept_user_terms_and_conditions(user)
    except Exception as e:
        logger.exception("auth.accept_terms_and_conditions")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
