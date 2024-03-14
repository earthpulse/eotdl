from pydantic import BaseModel, validator
from typing import List
import markdownify
from pathlib import Path


class Metadata(BaseModel):
    authors: List[str]
    license: str
    source: str
    name: str
    thumbnail: str

    # validate source is a URL
    @validator("source")
    def source_is_url(cls, v):
        if not v.startswith("http") and not v.startswith("https"):
            raise ValueError("source must be a URL")
        return v

    # validate thumbnail is a url
    @validator("thumbnail")
    def thumbnail_is_url(cls, v):
        if not v.startswith("http") and not v.startswith("https"):
            raise ValueError("thumbnail must be a URL")
        return v


def generate_metadata(download_path, model):
    with open(download_path + "/README.md", "w") as f:
        f.write("---\n")
        f.write(f"name: {model['name']}\n")
        f.write(f"license: {model['license']}\n")
        f.write(f"source: {model['source']}\n")
        f.write(f"thumbnail: {model['thumbnail']}\n")
        f.write(f"authors:\n")
        for author in model["authors"]:
            f.write(f"  - {author}\n")
        f.write("---\n")
        f.write(markdownify.markdownify(model["description"], heading_style="ATX"))
    # remove metadata.yml if exists
    if Path(download_path + "/metadata.yml").exists():
        Path(download_path + "/metadata.yml").unlink()
    return download_path + "/README.md"
