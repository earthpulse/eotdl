from pydantic import BaseModel, validator
from typing import List, Optional
import markdownify
from pathlib import Path


class Metadata(BaseModel):
    authors: List[str]
    license: str
    source: str
    name: str
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
        if not v.startswith("http") and not v.startswith("https"):
            raise ValueError("thumbnail must be a URL")
        return v


def generate_metadata(download_path, dataset):
    with open(download_path + "/README.md", "w") as f:
        f.write("---\n")
        f.write(f"name: {dataset['name']}\n")
        f.write(f"license: {dataset['license']}\n")
        f.write(f"source: {dataset['source']}\n")
        f.write(f"thumbnail: {dataset['thumbnail']}\n")
        f.write(f"authors:\n")
        for author in dataset["authors"]:
            f.write(f"  - {author}\n")
        f.write("---\n")
        f.write(markdownify.markdownify(dataset["description"], heading_style="ATX"))
    # remove metadata.yml if exists
    if Path(download_path + "/metadata.yml").exists():
        Path(download_path + "/metadata.yml").unlink()
    return download_path + "/README.md"
