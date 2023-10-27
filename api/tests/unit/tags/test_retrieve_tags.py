import pytest 
from unittest.mock import patch

from ....src.usecases.tags import retrieve_tags 

@patch('api.src.usecases.tags.retrieve_tags.TagsDBRepo')
def test_retrieve_tags(mocked_repo):
    mocked_repo_instance = mocked_repo.return_value
    mocked_repo_instance.retrieve_tags.return_value = [{'name': 'tag1'}, {'name': 'tag2'}]
    result = retrieve_tags()
    assert result == ['tag1', 'tag2']
    mocked_repo_instance.retrieve_tags.assert_called_once()
    
@patch('api.src.usecases.tags.retrieve_tags.TagsDBRepo')
def test_retrieve_tags_fail(mocked_repo):
    mocked_repo_instance = mocked_repo.return_value
    mocked_repo_instance.retrieve_tags.return_value = [{'name': 'tag1'}, {'kk': 'tag2'}]
    with pytest.raises(Exception):
        retrieve_tags()
    mocked_repo_instance.retrieve_tags.assert_called_once()
