from pydantic import BaseModel, validator
from datetime import datetime
from typing import List
import re
from ..errors import (
    NameCharsValidationError,
    NameLengthValidationError,
    DescriptionLengthValidationError,
)


def validate_name(
    name: str,
    regex: str = "^[^a-zA-Z]{1}|[^a-zA-Z0-9-]",
    max_length: int = 45,
    min_length: int = 3,
) -> str:
    if re.findall(regex, name):
        raise NameCharsValidationError()
    if len(name) > max_length or len(name) < min_length:
        raise NameLengthValidationError(max_length, min_length)
    return name


def validate_description(
    description: str, max_length: int = 50, min_length: int = 5
) -> str:
    if len(description) > max_length or len(description) < min_length:
        raise DescriptionLengthValidationError(max_length, min_length)
    return description


class File(BaseModel):
    name: str
    size: int
    checksum: str


class Dataset(BaseModel):
    uid: str
    id: str
    name: str
    size: int = 0
    files: List[File] = []
    description: str = ""
    tags: List[str] = []
    createdAt: datetime = datetime.now()
    updatedAt: datetime = datetime.now()
    likes: int = 0
    downloads: int = 0
    quality: int = 0
    author: str = ""
    link: str = ""
    license: str = ""

    @validator("name")
    def check_name_is_valid(cls, name):
        if name is not None:
            assert validate_name(name) == name
        return name


class UploadingFile(BaseModel):
    uid: str
    id: str
    upload_id: str
    name: str
    dataset: str
    checksum: str
    createdAt: datetime = datetime.now()
    updatedAt: datetime = datetime.now()
    parts: List[int] = []

    @validator("dataset")
    def check_name_is_valid(cls, dataset):
        if dataset is not None:
            assert validate_name(dataset) == dataset
        return dataset
