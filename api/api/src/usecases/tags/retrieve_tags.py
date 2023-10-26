from ...models import Tag
from ...repos import TagsDBRepo

def retrieve_tags():
    repo = TagsDBRepo()
    data = repo.retrieve_tags()
    tags = [Tag(**tag) for tag in data]
    names = [tag.name for tag in tags]
    return sorted(names)