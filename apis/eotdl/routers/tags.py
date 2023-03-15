from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status

from src.usecases.tags import retrieve_tags

router = APIRouter(
    prefix="/tags",
    tags=["tags"]
)

@router.get("")
def retrieve():
    try:
        return retrieve_tags()
    except Exception as e:
        print('ERROR tags:retrieve', str(e))
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
