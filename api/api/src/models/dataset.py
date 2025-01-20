from pydantic import BaseModel, field_validator, Field
from datetime import datetime
from typing import List

from .validators import validate_name
from .verison import Version


class Dataset(BaseModel):
    uid: str
    id: str
    name: str
    createdAt: datetime = Field(default_factory=datetime.now)
    updatedAt: datetime = Field(default_factory=datetime.now)
    catalog: dict = {} # contains license, source, authors, ...
    files: str
    versions: List[Version] = []
    description: str = ""
    tags: List[str] = []
    size: int = 0
    likes: int = 0
    downloads: int = 0
    quality: int = 0

    @field_validator("name")
    def check_name_is_valid(cls, name):
        if name is not None:
            assert validate_name(name) == name
        return name