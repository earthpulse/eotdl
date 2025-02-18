from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends
import logging

from ..auth import get_current_user
from ...src.usecases.notifications import retrieve_notifications, accept_notification, decline_notification
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

@router.post("/{id}/accept")
def accept(
    id: str,
    user: User = Depends(get_current_user),
):
    try:
        return accept_notification(id, user)
    except Exception as e:
        logger.exception("notification:accept")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    
@router.post("/{id}/decline")
def decline(
    id: str,
    user: User = Depends(get_current_user),
):
    try:
        return decline_notification(id, user)
    except Exception as e:
        logger.exception("notification:decline")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
