from pydantic import BaseModel, field_validator, Field
from datetime import datetime
from typing import List

from .validators import validate_name
from .verison import Version
from .metadata import Metadata


class Model(BaseModel):
    uid: str
    id: str
    name: str
    metadata: Metadata
    versions: List[Version] = [Version(version_id=1)]
    tags: List[str] = []
    createdAt: datetime = Field(default_factory=datetime.now)
    updatedAt: datetime = Field(default_factory=datetime.now)
    likes: int = 0
    downloads: int = 0
    quality: int = 0
    active: bool = True

    @field_validator("name")
    def check_name_is_valid(cls, name):
        if name is not None:
            assert validate_name(name) == name
        return name