import pytest
from unittest import mock

from ....src.usecases.datasets.IngestDataset import IngestDataset


def test_ingest_dataset_fails_if_tier_limits_surpassed():
    db_repo = mock.Mock()
    db_repo.retrieve.return_value = {
        "uid": "123",
        "email": "test",
        "name": "test",
        "picture": "test",
        "tier": "free",
    }
    tier = {"name": "dev", "limits": {"datasets": {"upload": 10, "download": 100}}}
    db_repo.find_one_by_name.return_value = tier
    db_repo.find_in_time_range.return_value = [1] * 100
    os_repo = mock.Mock()
    retrieve = IngestDataset(db_repo, os_repo)
    inputs = IngestDataset.Inputs(
        name="test", description="test", file=None, uid="123", size=123
    )
    with pytest.raises(Exception):
        retrieve(inputs)
