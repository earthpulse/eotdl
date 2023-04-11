from pydantic import BaseModel
from typing import List

from ...models import Tag

class RetrieveTags():
    def __init__(self, repo):
        self.repo = repo

    class Inputs(BaseModel):
        pass

    class Outputs(BaseModel):
        tags: List[str]

    def __call__(self, inputs: Inputs) -> Outputs:
        data = self.repo.retrieve('tags')
        tags = [Tag(**tag) for tag in data]
        names = [tag.name for tag in tags]
        return self.Outputs(tags=sorted(names))