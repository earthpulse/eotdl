from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends, File, Form, UploadFile
import aiofiles
from fastapi.responses import StreamingResponse

from src.models import User
from src.usecases.datasets import ingest_dataset, retrieve_datasets, retrieve_dataset_by_name, download_dataset
from .auth import get_current_user

router = APIRouter(
    prefix="/datasets",
    tags=["datasets"]
)

@router.post("")
def ingest(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: str = Form(...),
    user: User = Depends(get_current_user),
):
    try:
        return ingest_dataset(file.file, name, description, user)
    except Exception as e:
        print('ERROR datasets:ingest', str(e))
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.get("")
def retrieve(
    name: str = None,
):
    try:
        if name is None:
            return retrieve_datasets()
        return retrieve_dataset_by_name(name)
    except Exception as e:
        print('ERROR datasets:retrieve', str(e))
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))



@router.get("/{id}/download")
async def download(
    id: str ,
    # user: User = Depends(get_current_user),
):
    try:
        data_stream, object_info, name = download_dataset(id, None)
        response_headers = {
            "Content-Disposition": f'attachment; filename="{name}.zip"',
            "Content-Type": "application/zip",
            "Content-Length": str(object_info.size),
        }
        return StreamingResponse(data_stream(id), headers=response_headers, media_type=object_info.content_type)
    except Exception as e:
        print('ERROR datasets:download', str(e))
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))