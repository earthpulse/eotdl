from pydantic import BaseModel
from datetime import datetime
from typing import List

class Dataset(BaseModel):
    uid: str
    id: str
    name: str
    description: str
    tags: List[str] = []
    createdAt: datetime = datetime.now()
    updatedAt: datetime = datetime.now()