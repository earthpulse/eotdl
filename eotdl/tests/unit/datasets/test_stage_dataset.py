from unittest import mock

import pandas as pd
import pytest

import eotdl.datasets.stage as stage_module


@pytest.fixture
def dataset():
    return {
        "id": "dataset-id",
        "name": "my-dataset",
        "metadata": {
            "authors": ["Albert"],
            "license": "CC-BY-4.0",
            "source": "https://example.com",
            "description": "desc",
            "thumbnail": "",
        },
        "versions": [{"version_id": 1}],
    }


@pytest.fixture
def catalog_rows():
    return pd.DataFrame(
        [
            {
                "id": "clearsar.ipynb",
                "assets": {
                    "asset": {
                        "href": "https://api.eotdl.com/datasets/dataset-id/stage/clearsar.ipynb-470630"
                    }
                },
            },
            {
                "id": "tile",
                "assets": {
                    "rgb": {"href": "https://api.eotdl.com/datasets/dataset-id/stage/tile_rgb-123"},
                    "nir": {"href": "https://api.eotdl.com/datasets/dataset-id/stage/tile_nir-456"},
                },
            },
            {
                "id": None,
                "assets": {
                    "asset": {"href": "https://api.eotdl.com/datasets/dataset-id/stage/legacy-name-999"}
                },
            },
        ]
    )


def test_stage_dataset_uses_logical_asset_names(dataset, catalog_rows, tmp_path):
    class FakeFilesAPIRepo:
        def stage_file(
            self,
            dataset_id,
            file_name,
            user,
            download_path,
            endpoint="datasets",
            progress=False,
        ):
            catalog_path = tmp_path / "catalog.v1.parquet"
            catalog_path.write_bytes(b"catalog")
            return str(catalog_path)

    staged_calls = []

    with (
        mock.patch("eotdl.auth.auth.auth", return_value={"id_token": "token"}),
        mock.patch.object(stage_module, "retrieve_dataset", return_value=dataset),
        mock.patch.object(stage_module, "FilesAPIRepo", return_value=FakeFilesAPIRepo()),
        mock.patch.object(stage_module.gpd, "read_parquet", return_value=catalog_rows),
        mock.patch.object(
            stage_module,
            "stage_dataset_file",
            side_effect=lambda file_url, path, output_name=None: staged_calls.append(
                (file_url, output_name)
            ),
        ),
    ):
        stage_module.stage_dataset("my-dataset", assets=True, path=str(tmp_path / "downloads"))

    assert staged_calls == [
        (
            "https://api.eotdl.com/datasets/dataset-id/stage/clearsar.ipynb-470630",
            "clearsar.ipynb",
        ),
        (
            "https://api.eotdl.com/datasets/dataset-id/stage/tile_rgb-123",
            "tile_rgb",
        ),
        (
            "https://api.eotdl.com/datasets/dataset-id/stage/tile_nir-456",
            "tile_nir",
        ),
        (
            "https://api.eotdl.com/datasets/dataset-id/stage/legacy-name-999",
            None,
        ),
    ]
