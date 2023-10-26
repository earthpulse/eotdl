from pydantic import BaseModel
from datetime import datetime


class Version(BaseModel):
    version_id: int
    createdAt: datetime = datetime.now()
    size: int = 0
