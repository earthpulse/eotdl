from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import List

<<<<<<< HEAD:apis/eotdl/src/models/dataset.py

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
=======
from .validators import validate_name
from .verison import Version
>>>>>>> develop:api/api/src/models/dataset.py


class Dataset(BaseModel):
    uid: str
    id: str
    name: str
<<<<<<< HEAD:apis/eotdl/src/models/dataset.py
    description: str
=======
    authors: List[str]
    source: str
    license: str
    files: str
    versions: List[Version] = []
    description: str = ""
>>>>>>> develop:api/api/src/models/dataset.py
    tags: List[str] = []
    createdAt: datetime = datetime.now()
    updatedAt: datetime = datetime.now()
    likes: int = 0
    downloads: int = 0
    quality: int = 0
    size: int = 0

    @field_validator("name")
    def check_name_is_valid(cls, name):
        if name is not None:
            assert validate_name(name) == name
        return name
<<<<<<< HEAD:apis/eotdl/src/models/dataset.py
=======

    @field_validator("source")
    def check_source_is_url(cls, source):
        if source != "" and source is not None:
            if not source.startswith("http") and not source.startswith("https"):
                raise ValueError("source must be a valid url")
        return source


class STACDataset(BaseModel):
    uid: str
    id: str
    name: str
    description: str = ""
    tags: List[str] = []
    createdAt: datetime = datetime.now()
    updatedAt: datetime = datetime.now()
    likes: int = 0
    downloads: int = 0
    quality: int = 1
    size: int = 0
    catalog: dict = {}
    versions: List[Version] = []
    files: str

    # @validator("name")
    # def check_name_is_valid(cls, name):
    #     if name is not None:
    #         assert validate_name(name) == name
    #     return name
>>>>>>> develop:api/api/src/models/dataset.py
