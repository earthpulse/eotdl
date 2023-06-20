import pytest 
from unittest import mock

from ....src.usecases.datasets.EditDataset import EditDataset
from ....src.errors import InvalidTagError, DatasetDoesNotExistError, UserUnauthorizedError, DatasetAlreadyExistsError

@pytest.fixture
def user():
    return {'uid': '123', 'email': 'test', 'name': 'test', 'picture': 'test', 'tier': 'free'}

@pytest.fixture
def datasets():
    return [
        {'uid': '123', 'id': '123', 'name': 'test', 'description': 'test'},
        {'uid': '456', 'id': '456', 'name': 'test2', 'description': 'test 2'},
    ]        

def test_edit_dataset_fails_if_dataset_not_found():
    db_repo = mock.Mock()
    db_repo.retrieve.return_value = None
    edit = EditDataset(db_repo, None)
    inputs = EditDataset.Inputs(id="123", uid="123")
    with pytest.raises(DatasetDoesNotExistError):
        edit(inputs)
    db_repo.retrieve.assert_called_once_with('datasets', '123', '_id')
    
def test_edit_dataset_fails_if_user_does_not_own_dataset(user, datasets):
    db_repo = mock.Mock()
    db_repo.retrieve.return_value = datasets[1]
    edit = EditDataset(db_repo, None)
    inputs = EditDataset.Inputs(id="456", uid="123")
    with pytest.raises(UserUnauthorizedError):
        edit(inputs)
    db_repo.retrieve.assert_called_once_with('datasets', '456', '_id')

def test_edit_dataset_fails_if_new_name_not_unique(user, datasets):
    db_repo = mock.Mock()
    db_repo.retrieve.return_value = datasets[0]
    db_repo.find_one_by_name.return_value = datasets[1]
    edit = EditDataset(db_repo, None)
    inputs = EditDataset.Inputs(id="123", uid="123", name="test2")
    with pytest.raises(DatasetAlreadyExistsError):
        edit(inputs)
    db_repo.find_one_by_name.assert_called_once_with('datasets', 'test2')

def test_edit_dataset_fails_if_tags_not_valid(user, datasets):
    db_repo = mock.Mock()
    db_repo.retrieve.return_value = datasets[0]
    db_repo.find_one_by_name.return_value = None
    retrieve_tags = mock.Mock()
    retrieve_tags.return_value = ['d', 'e']
    edit = EditDataset(db_repo, retrieve_tags)
    inputs = EditDataset.Inputs(id="123", uid="123", tags=['a', 'b'])
    with pytest.raises(InvalidTagError):
        edit(inputs)

def test_edit_dataset(user, datasets):
    db_repo = mock.Mock()
    db_repo.retrieve.return_value = datasets[0]
    db_repo.find_one_by_name.return_value = None
    retrieve_tags = mock.Mock()
    retrieve_tags.return_value = ['a', 'b']
    edit = EditDataset(db_repo, retrieve_tags)
    inputs = EditDataset.Inputs(id="123", uid="123", name="test3", description="test 3", tags=['a'])
    outputs = edit(inputs)
    assert outputs.dataset.id == "123"
    assert outputs.dataset.name == "test3"
    assert outputs.dataset.description == "test 3"
    assert outputs.dataset.tags == ['a']
    db_repo.update.assert_called_once_with('datasets', '123', outputs.dataset.dict())
    # update only name
    inputs = EditDataset.Inputs(id="123", uid="123", name="test3")
    outputs = edit(inputs)
    assert outputs.dataset.id == "123"
    assert outputs.dataset.name == "test3"
    assert outputs.dataset.description == "test"
    assert outputs.dataset.tags == []
    # update only description
    inputs = EditDataset.Inputs(id="123", uid="123", description="test 3")
    outputs = edit(inputs)
    assert outputs.dataset.id == "123"
    assert outputs.dataset.name == "test"
    assert outputs.dataset.description == "test 3"
    assert outputs.dataset.tags == []
    # update only tags
    inputs = EditDataset.Inputs(id="123", uid="123", tags=['a'])
    outputs = edit(inputs)
    assert outputs.dataset.id == "123"
    assert outputs.dataset.name == "test"
    assert outputs.dataset.description == "test"
    assert outputs.dataset.tags == ['a']