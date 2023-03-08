from fastapi import APIRouter

from eotdl import say_hello

router = APIRouter(
    prefix="/hello",
    tags=["hello"]
)

@router.get("/")
async def root():
    return say_hello()