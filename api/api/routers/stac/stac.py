from fastapi import APIRouter
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("")
def stac():
    return {"message": "Welcome to the STAC API"}
    