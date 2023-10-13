from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
import logging
from pydantic import BaseModel

from ...src.usecases.user import update_user
from ...src.models import User
from .main import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

class UpdateData(BaseModel):
    name: str


@router.post("", include_in_schema=False)
def update_user_data(
    data: UpdateData,
    user: User = Depends(get_current_user),
):
    try:
        return update_user(user, data.model_dump())
    except Exception as e:
        logger.exception("auth.update")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
