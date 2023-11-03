import os

from datetime import datetime
from eotdl.curation import STACDataFrame
from eotdl.curation.stac.dataframe import read_stac

from .fixtures import tmp_stac_catalog, tmp_stac_collection


output_path = "tmp/output_path"


def test_from_stac_file(tmp_stac_catalog):
    df = STACDataFrame.from_stac_file(tmp_stac_catalog)
    assert isinstance(df, STACDataFrame)


def test_to_stac(tmp_stac_catalog):
    df = STACDataFrame.from_stac_file(tmp_stac_catalog)
    df.to_stac(output_path)
    assert os.path.exists(output_path)


def test_curate_json_row():
    sample_row = {
        "created_at": datetime.now(),
        "modified_at": datetime.now(),
        "stac_id": "123",
        "id": "456",
    }
    curated_row = STACDataFrame().curate_json_row(sample_row, True)
    # Assertions to ensure unnecessary keys are removed, "id" key exists, etc.
    assert "id" in curated_row
    assert "stac_id" not in curated_row


def test_read_stac(tmp_stac_catalog):
    df = read_stac(tmp_stac_catalog)
    assert isinstance(df, STACDataFrame)
