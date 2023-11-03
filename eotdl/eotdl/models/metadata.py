from pydantic import BaseModel, validator
from typing import List


class Metadata(BaseModel):
    authors: List[str]
    license: str
    source: str
    name: str

    # validate source is a URL
    @validator("source")
    def source_is_url(cls, v):
        if not v.startswith("http") and not v.startswith("https"):
            raise ValueError("source must be a URL")
        return v
