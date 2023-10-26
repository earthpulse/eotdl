import pytest
from unittest import mock

from ....src.usecases.datasets.upload_large_file import GenerateUploadId
from ....src.errors import DatasetAlreadyExistsError, TierLimitError


@pytest.fixture
def user():
    return {
        "uid": "123",
        "email": "test",
        "name": "test",
        "picture": "test",
        "tier": "dev",
    }


@pytest.fixture
def tier():
    return {
        "name": "dev",
        "limits": {
            "datasets": {"upload": 10, "download": 100, "count": 10, "files": 10}
        },
    }


@pytest.fixture
def dataset():
    return {"uid": "123", "id": "123", "name": "test-dataset-name"}


def test_generate_upload_id_for_new_upload_to_new_dataset(user, tier, dataset):
    db_repo, os_repo, s3_repo = mock.Mock(), mock.Mock(), mock.Mock()
    db_repo.find_one.return_value = None  # new upload
    db_repo.retrieve.return_value = user
    db_repo.find_one_by_name.side_effect = [tier, None]  # new dataset
    db_repo.find_in_time_range.return_value = []
    db_repo.generate_id.return_value = "123"
    os_repo.get_object.return_value = "test-storage"
    s3_repo.multipart_upload_id.return_value = "test_upload_id"
    retrieve = GenerateUploadId(db_repo, os_repo, s3_repo)
    inputs = GenerateUploadId.Inputs(
        name="test-file-name", dataset="test-dataset-name", uid="123", checksum="123"
    )
    outputs = retrieve(inputs)
    assert outputs.upload_id == "test_upload_id"
    assert outputs.parts == []
    db_repo.find_one.assert_called_once_with(
        "uploading",
        {"uid": "123", "name": "test-file-name", "dataset": "test-dataset-name"},
    )
    db_repo.retrieve.assert_called_once_with("users", "123", "uid")
    assert db_repo.find_one_by_name.call_count == 2
    call_args_list = db_repo.find_one_by_name.call_args_list
    assert call_args_list[0][0] == ("tiers", "dev")
    assert call_args_list[1][0] == ("datasets", "test-dataset-name")
    db_repo.find_in_time_range.assert_called_once_with(
        "usage", "123", "dataset_ingested", "type"
    )
    db_repo.generate_id.assert_called_once_with()
    os_repo.get_object.assert_called_once_with("123", "test-file-name")
    s3_repo.multipart_upload_id.assert_called_once_with("test-storage")
    db_repo.persist.assert_called_once()
    db_repo.delete.assert_not_called()


@pytest.fixture
def uploading():
    return {
        "uid": "123",
        "id": "123",
        "upload_id": "test_upload_id",
        "name": "test-file-name",
        "dataset": "test-dataset-name",
        "checksum": "123",
        "parts": [1, 2, 3],
    }


def test_retrieve_upload_id_for_existing_upload(uploading):
    db_repo, os_repo, s3_repo = mock.Mock(), mock.Mock(), mock.Mock()
    db_repo.find_one.return_value = uploading  # existing upload
    retrieve = GenerateUploadId(db_repo, os_repo, s3_repo)
    inputs = GenerateUploadId.Inputs(
        name="test-file-name", dataset="test-dataset-name", uid="123", checksum="123"
    )
    outputs = retrieve(inputs)
    assert outputs.upload_id == "test_upload_id"
    assert outputs.parts == [1, 2, 3]
    db_repo.delete.assert_not_called()
    db_repo.retrieve.assert_not_called()


def test_generate_upload_id_for_existing_upload_with_new_file(user, tier, uploading):
    db_repo, os_repo, s3_repo = mock.Mock(), mock.Mock(), mock.Mock()
    db_repo.find_one.return_value = uploading  # existing upload
    db_repo.retrieve.return_value = user
    db_repo.find_one_by_name.side_effect = [tier, None]  # new dataset
    db_repo.find_in_time_range.return_value = []
    db_repo.generate_id.return_value = "123"
    os_repo.get_object.return_value = "test-storage"
    s3_repo.multipart_upload_id.return_value = "test_upload_id"
    retrieve = GenerateUploadId(db_repo, os_repo, s3_repo)
    inputs = GenerateUploadId.Inputs(
        name="test-file-name", dataset="test-dataset-name", uid="123", checksum="456"
    )
    outputs = retrieve(inputs)
    assert outputs.upload_id == "test_upload_id"
    assert outputs.parts == []
    db_repo.find_one.assert_called_once_with(
        "uploading",
        {"uid": "123", "name": "test-file-name", "dataset": "test-dataset-name"},
    )
    db_repo.retrieve.assert_called_once_with("users", "123", "uid")
    assert db_repo.find_one_by_name.call_count == 2
    call_args_list = db_repo.find_one_by_name.call_args_list
    assert call_args_list[0][0] == ("tiers", "dev")
    assert call_args_list[1][0] == ("datasets", "test-dataset-name")
    db_repo.find_in_time_range.assert_called_once_with(
        "usage", "123", "dataset_ingested", "type"
    )
    db_repo.generate_id.assert_called_once_with()
    os_repo.get_object.assert_called_once_with("123", "test-file-name")
    s3_repo.multipart_upload_id.assert_called_once_with("test-storage")
    db_repo.persist.assert_called_once()
    db_repo.delete.assert_called_once_with("uploading", "123")


def test_generate_upload_id_for_new_upload_to_existing_dataset(user, tier, dataset):
    db_repo, os_repo, s3_repo = mock.Mock(), mock.Mock(), mock.Mock()
    db_repo.find_one.return_value = None  # new upload
    db_repo.retrieve.return_value = user
    db_repo.find_one_by_name.side_effect = [tier, dataset]  # existing dataset
    # db_repo.find_in_time_range.return_value = []
    db_repo.generate_id.return_value = "123"
    os_repo.get_object.return_value = "test-storage"
    s3_repo.multipart_upload_id.return_value = "test_upload_id"
    retrieve = GenerateUploadId(db_repo, os_repo, s3_repo)
    inputs = GenerateUploadId.Inputs(
        name="test-file-name", dataset="test-dataset-name", uid="123", checksum="456"
    )
    outputs = retrieve(inputs)
    assert outputs.upload_id == "test_upload_id"
    assert outputs.parts == []
    db_repo.find_one.assert_called_once_with(
        "uploading",
        {"uid": "123", "name": "test-file-name", "dataset": "test-dataset-name"},
    )
    db_repo.retrieve.assert_called_once_with("users", "123", "uid")
    assert db_repo.find_one_by_name.call_count == 2
    call_args_list = db_repo.find_one_by_name.call_args_list
    assert call_args_list[0][0] == ("tiers", "dev")
    assert call_args_list[1][0] == ("datasets", "test-dataset-name")
    db_repo.find_in_time_range.assert_not_called()
    db_repo.generate_id.assert_called_once_with()
    os_repo.get_object.assert_called_once_with("123", "test-file-name")
    s3_repo.multipart_upload_id.assert_called_once_with("test-storage")
    db_repo.persist.assert_called_once()
    db_repo.delete.assert_not_called()


def test_generate_upload_id_for_new_upload_to_existing_dataset_should_fail_if_user_is_not_owner(
    user, tier, dataset
):
    db_repo, os_repo, s3_repo = mock.Mock(), mock.Mock(), mock.Mock()
    db_repo.find_one.return_value = None  # new upload
    db_repo.retrieve.return_value = user
    dataset["uid"] = "someone_else"
    db_repo.find_one_by_name.side_effect = [tier, dataset]  # existing dataset
    # db_repo.find_in_time_range.return_value = []
    db_repo.generate_id.return_value = "123"
    os_repo.get_object.return_value = "test-storage"
    s3_repo.multipart_upload_id.return_value = "test_upload_id"
    retrieve = GenerateUploadId(db_repo, os_repo, s3_repo)
    inputs = GenerateUploadId.Inputs(
        name="test-file-name", dataset="test-dataset-name", uid="123", checksum="456"
    )
    with pytest.raises(DatasetAlreadyExistsError):
        outputs = retrieve(inputs)


def test_generate_upload_id_for_new_upload_to_existing_dataset_should_fail_if_limits(
    user, tier, dataset
):
    db_repo, os_repo, s3_repo = mock.Mock(), mock.Mock(), mock.Mock()
    db_repo.find_one.return_value = None  # new upload
    db_repo.retrieve.return_value = user
    tier["limits"]["datasets"]["files"] = 0
    db_repo.find_one_by_name.side_effect = [tier, dataset]  # existing dataset
    # db_repo.find_in_time_range.return_value = []
    db_repo.generate_id.return_value = "123"
    os_repo.get_object.return_value = "test-storage"
    s3_repo.multipart_upload_id.return_value = "test_upload_id"
    retrieve = GenerateUploadId(db_repo, os_repo, s3_repo)
    inputs = GenerateUploadId.Inputs(
        name="test-file-name", dataset="test-dataset-name", uid="123", checksum="456"
    )
    with pytest.raises(TierLimitError):
        outputs = retrieve(inputs)


def test_generate_upload_id_for_new_upload_to_new_dataset_should_fail_if_limits_upload(
    user, tier, dataset
):
    db_repo, os_repo, s3_repo = mock.Mock(), mock.Mock(), mock.Mock()
    db_repo.find_one.return_value = None  # new upload
    db_repo.retrieve.return_value = user
    tier["limits"]["datasets"]["upload"] = 2
    db_repo.find_one_by_name.side_effect = [tier, None]  # new dataset
    db_repo.find_in_time_range.return_value = [1, 2, 3]
    db_repo.generate_id.return_value = "123"
    os_repo.get_object.return_value = "test-storage"
    s3_repo.multipart_upload_id.return_value = "test_upload_id"
    retrieve = GenerateUploadId(db_repo, os_repo, s3_repo)
    inputs = GenerateUploadId.Inputs(
        name="test-file-name", dataset="test-dataset-name", uid="123", checksum="456"
    )
    with pytest.raises(TierLimitError):
        outputs = retrieve(inputs)


def test_generate_upload_id_for_new_upload_to_new_dataset_should_fail_if_limits_count(
    user, tier, dataset
):
    db_repo, os_repo, s3_repo = mock.Mock(), mock.Mock(), mock.Mock()
    db_repo.find_one.return_value = None  # new upload
    user["dataset_count"] = 10
    db_repo.retrieve.return_value = user
    tier["limits"]["datasets"]["count"] = 3
    db_repo.find_one_by_name.side_effect = [tier, None]  # new dataset
    db_repo.find_in_time_range.return_value = []
    db_repo.generate_id.return_value = "123"
    os_repo.get_object.return_value = "test-storage"
    s3_repo.multipart_upload_id.return_value = "test_upload_id"
    retrieve = GenerateUploadId(db_repo, os_repo, s3_repo)
    inputs = GenerateUploadId.Inputs(
        name="test-file-name", dataset="test-dataset-name", uid="123", checksum="456"
    )
    with pytest.raises(TierLimitError):
        outputs = retrieve(inputs)
