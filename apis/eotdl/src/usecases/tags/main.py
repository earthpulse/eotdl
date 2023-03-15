from ...repos import DBRepo
from .RetrieveTags import RetrieveTags

def retrieve_tags():
    repo = DBRepo()
    retrieve = RetrieveTags(repo)
    inputs = retrieve.Inputs()
    outputs = retrieve(inputs)
    return outputs.tags
