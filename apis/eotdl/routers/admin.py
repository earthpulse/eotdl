from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
import logging
import os

from .auth import key_auth

logger=logging.getLogger(__name__)

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

@router.get("/logs/{tail}", include_in_schema=False)
def logs(isAdmin: bool = Depends(key_auth), tail: int = 10):
    try:
        # return last lines of log file
        with open('/tmp/eotdl-api.log', 'r') as f:
            lines = f.readlines()
            return lines[-tail:]            
    except Exception as e:
        logger.exception('logs')
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e))
    
@router.get("/env", include_in_schema=False)
def logs(isAdmin: bool = Depends(key_auth)):
    try:
        return os.environ
    except Exception as e:
        logger.exception('logs')
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e))