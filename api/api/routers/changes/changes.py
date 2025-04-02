from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends
import logging
import traceback

from ..auth import get_current_user
from ...src.usecases.changes import retrieve_change, accept_change, decline_change
from ...src.models import User

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/{change_id}")
def retrieve(
    change_id: str,
    user: User = Depends(get_current_user),
):
    try:
        return retrieve_change(change_id, user)
    except Exception as e:
        traceback.print_exc()
        logger.exception("changes:retrieve")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.post("/{change_id}/accept")
def accept(
    change_id: str,
    user: User = Depends(get_current_user),
):
    try:
        return accept_change(change_id, user)
    except Exception as e:
        traceback.print_exc()
        logger.exception("changes:accept")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.post("/{change_id}/decline")
def decline(
    change_id: str,
    user: User = Depends(get_current_user),
):
    try:
        return decline_change(change_id, user)
    except Exception as e:
        traceback.print_exc()
        logger.exception("changes:decline")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
