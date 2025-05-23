from pydantic import BaseModel, validator
from typing import List, Optional
from pathlib import Path
import os

class Metadata(BaseModel):
    authors: List[str]
    license: str
    source: str
    name: str
    description: str
    thumbnail: Optional[str] = ""

    # validate source is a URL
    @validator("source")
    def source_is_url(cls, v):
        if not v.startswith("http") and not v.startswith("https"):
            raise ValueError("source must be a URL")
        return v

    # validate thumbnail is a url
    @validator("thumbnail")
    def thumbnail_is_url(cls, v):
        if not v:
            return ""
        if not v.startswith("http") and not v.startswith("https"):
            raise ValueError("thumbnail must be a URL")
        return v


    def save_metadata(self, dst_path):
        os.makedirs(dst_path, exist_ok=True)
        with open(Path(dst_path) / "README.md", "w") as f:
            f.write("---\n")
            f.write(f"name: {self.name}\n")
            f.write(f"license: {self.license}\n") 
            f.write(f"source: {self.source}\n")
            if self.thumbnail:
                f.write(f"thumbnail: {self.thumbnail}\n")
            f.write(f"authors:\n")
            for author in self.authors:
                f.write(f"  - {author}\n")
            f.write("---\n")
            f.write(self.description)
        return str(Path(dst_path) / "README.md")