from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class File(BaseModel):
    name: str
    size: int
    checksum: str
    version: int
    versions: List[int] = []
    createdAt: datetime = datetime.now()


class Folder(BaseModel):
    name: str
    versions: List[int] = []


class Files(BaseModel):
    id: str
    dataset: str
    files: List[File] = []
    folders: List[Folder] = []
    createdAt: datetime = datetime.now()
    updatedAt: datetime = datetime.now()


class UploadingFile(BaseModel):
    uid: str
    id: str
    upload_id: str
    filename: str
    version: int
    dataset: Optional[str] = None
    model: Optional[str] = None
    checksum: str
    createdAt: datetime = datetime.now()
    updatedAt: datetime = datetime.now()
    parts: List[int] = []
