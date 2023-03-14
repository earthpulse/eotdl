from pydantic import BaseModel
from datetime import datetime

class Dataset(BaseModel):
    uid: str
    id: str
    name: str
    createdAt: datetime = datetime.now()
    updatedAt: datetime = datetime.now()