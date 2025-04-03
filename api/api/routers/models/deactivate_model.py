from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status
import logging

from ...src.usecases.models import deactivate_model

router = APIRouter()
logger = logging.getLogger(__name__)


@router.patch("/{name}", include_in_schema=False)
def deactivate(
    name: str,
):
    try:
        message = deactivate_model(name)
        return {"message": message}
    except Exception as e:
        logger.exception("models:deactivate")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
