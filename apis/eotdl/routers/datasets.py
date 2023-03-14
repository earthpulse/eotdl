from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends, File, Form, UploadFile

from src.models import User
from src.usecases.datasets import ingest_dataset
from .auth import get_current_user

router = APIRouter(
    prefix="/datasets",
    tags=["datasets"]
)

@router.post("/ingest")
def ingest(
    file: UploadFile = File(...),
    name: str = Form(...),
    user: User = Depends(get_current_user),
):
    try:
        return ingest_dataset(file, name, user)
    except Exception as e:
        print('ERROR datasets:ingest', str(e))
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
