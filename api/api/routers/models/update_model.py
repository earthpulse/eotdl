from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends
import logging

from ..auth import get_current_user
from ...src.models import User
from ...src.usecases.models import toggle_like_model

router = APIRouter()
logger = logging.getLogger(__name__)


@router.put("/{id}/like", include_in_schema=False)
def like(
    id: str,
    user: User = Depends(get_current_user),
):
    try:
        return toggle_like_model(id, user)
    except Exception as e:
        logger.exception("models:like")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
