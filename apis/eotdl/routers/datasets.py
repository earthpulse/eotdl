from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends, File, Form, UploadFile, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Union

from src.models import User
from src.usecases.datasets import ingest_dataset_chunk, retrieve_liked_datasets, like_dataset, ingest_dataset, retrieve_datasets, retrieve_popular_datasets, retrieve_dataset_by_name, download_dataset, edit_dataset, retrieve_datasets_leaderboard
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
    # if file.size > 100000000: # 100 MB
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File size too large, use the CLI to upload large files")
    try:
        return ingest_dataset(file.file, name, description, user)
    except Exception as e:
        print('ERROR datasets:ingest', str(e))
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.post("/chunk", include_in_schema=False)
def ingest_large(
    request: Request,
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    id: Optional[str] = Form(None),
    user: User = Depends(get_current_user),
):
    try:
        content_range = request.headers.get('content-range')
        ab, total = content_range.split(' ')[1].split('/')
        a, b = ab.split('-')
        is_last = int(b) == int(total) - 1
        dataset, id = ingest_dataset_chunk(file, name, description, user, total, id, is_last)
        return {'dataset': dataset, 'id': id}
    except Exception as e:
        print('ERROR datasets:ingest_large', str(e))
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.get("")
def retrieve(
    name: str = None,
    limit: Union[int,None] = None
):
    try:
        if name is None:
            return retrieve_datasets(limit)
        return retrieve_dataset_by_name(name, limit)
    except Exception as e:
        print('ERROR datasets:retrieve', str(e))
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.get("/liked", include_in_schema=False)
def retrieve(
    user: User = Depends(get_current_user),
):
    try:
        return retrieve_liked_datasets(user)
    except Exception as e:
        print('ERROR datasets:retrieve', str(e))
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/popular", include_in_schema=False)
def retrieve(
    limit: Union[int,None] = None
):
    try:
        return retrieve_popular_datasets(limit)
    except Exception as e:
        print('ERROR datasets:retrieve', str(e))
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.get("/{id}/download")
async def download(
    id: str ,
    user: User = Depends(get_current_user),
):
    try:
        data_stream, object_info, name = download_dataset(id, user)
        response_headers = {
            "Content-Disposition": f'attachment; filename="{name}.zip"',
            "Content-Type": "application/zip",
            "Content-Length": str(object_info.size),
        }
        return StreamingResponse(data_stream(id), headers=response_headers, media_type=object_info.content_type)
    except Exception as e:
        print('ERROR datasets:download', str(e))
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    
class EditBody(BaseModel):
    name: Optional[str]
    description: Optional[str]
    tags: Optional[List[str]]


@router.post("/{id}")
def edit(
    id: str,
    body: EditBody,
    user: User = Depends(get_current_user),
):
    try:
        return edit_dataset(id, body.name, body.description, body.tags, user)
    except Exception as e:
        print('ERROR datasets:edit', str(e))
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    
@router.get("/leaderboard", include_in_schema=False)
def leaderboard():
    try:
        return retrieve_datasets_leaderboard()
    except Exception as e:
        print('ERROR datasets:retrieve', str(e))
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    
@router.post("/{id}/like", include_in_schema=False)
def edit(
    id: str,
    user: User = Depends(get_current_user),
):
    try:
        return like_dataset(id, user)
    except Exception as e:
        print('ERROR datasets:like', str(e))
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))