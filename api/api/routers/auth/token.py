from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException
import logging

from ...src.usecases.auth import generate_id_token

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/token")
def token(code: str):
    try:
        return generate_id_token(code)
    except Exception as e:
        logger.exception("token")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
