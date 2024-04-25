from pydantic import BaseModel, Field
from datetime import datetime


class Version(BaseModel):
    version_id: int
    createdAt: datetime = Field(default_factory=datetime.now)
    size: int = 0
