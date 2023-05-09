import pytest 
from unittest import mock

from ....src.usecases.tags.RetrieveTags import RetrieveTags

def test_retrieve_tags():
    repo = mock.Mock()
    tags = [{'name': 'tag1'}, {'name': 'tag2'}]
    repo.retrieve.return_value = tags
    retrieve = RetrieveTags(repo)
    inputs = RetrieveTags.Inputs()
    outputs = retrieve(inputs)
    assert outputs.tags == ['tag1', 'tag2']
    repo.retrieve.return_value = [] 
    outputs = retrieve(inputs)
    assert outputs.tags == []
    
def test_retrieve_tags_fail():
    repo = mock.Mock()
    tags = [{'name': 'tag1'}, {'kk': 'tag2'}]
    repo.retrieve.return_value = tags
    retrieve = RetrieveTags(repo)
    inputs = RetrieveTags.Inputs()
    with pytest.raises(Exception):
    	retrieve(inputs)