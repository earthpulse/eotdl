from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends
import logging

from ..auth import admin_key_auth
from ...src.usecases.models import delete_model

router = APIRouter()
logger = logging.getLogger(__name__)


@router.delete("/{name}", include_in_schema=False)
def delete(
    name: str,
    isAdmin: bool = Depends(admin_key_auth),  # only admin can delete models
):
    try:
        message = delete_model(name)
        return {"message": message}
    except Exception as e:
        logger.exception("models:delete")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
