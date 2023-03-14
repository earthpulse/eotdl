from fastapi import APIRouter

from eotdl import say_hello

router = APIRouter(
    prefix="/hello",
    tags=["hello"]
)

@router.get("/")
def root():
    return say_hello()