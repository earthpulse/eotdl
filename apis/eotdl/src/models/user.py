from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    uid: str
    name: str
    email: str
    picture: str
    createdAt: datetime = datetime.now()
    updatedAt: datetime = datetime.now()
    dataset_count: int = 0
    model_count: int = 0