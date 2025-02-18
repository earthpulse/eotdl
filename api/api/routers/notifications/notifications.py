from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends
import logging

from ..auth import get_current_user
from ...src.usecases.notifications import retrieve_notifications, dismiss_notification
from ...src.models import User

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("")
def retrieve(
    user: User = Depends(get_current_user),
):
    try:
        return retrieve_notifications(user)
    except Exception as e:
        logger.exception("notification:retrieve")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    
@router.post("/{id}/dismiss")
def dismiss(
    id: str,
    user: User = Depends(get_current_user),
):
    try:
        return dismiss_notification(id, user)
    except Exception as e:
        logger.exception("notification:dismiss")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
