from pydantic import BaseModel


class Tag(BaseModel):
    name: str
    category: str
