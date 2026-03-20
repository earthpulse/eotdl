from unittest import mock

import pandas as pd

import eotdl.datasets.stage as stage_module


def test_stage_dataset_downloads_all_assets_in_parallel_path(monkeypatch, tmp_path):
    dataset = {
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
    gdf = pd.DataFrame(
        [
            {"assets": {"asset": {"href": "https://example.com/asset-1"}}},
            {
                "assets": {
                    "rgb": {"href": "https://example.com/asset-2"},
                    "nir": {"href": "https://example.com/asset-3"},
                }
            },
        ]
    )
    staged_urls = []

    class FakeFilesAPIRepo:
        def stage_file(
            self,
            dataset_or_model_id,
            file_name,
            user,
            path,
            endpoint="datasets",
            progress=False,
        ):
            catalog_path = tmp_path / "catalog.v1.parquet"
            catalog_path.write_bytes(b"catalog")
            return str(catalog_path)

        def stage_file_url(self, url, path, user):
            staged_urls.append(url)
            return str(tmp_path / "downloaded-file")

    monkeypatch.setenv("EOTDL_STAGE_WORKERS", "4")

    with (
        mock.patch("eotdl.auth.auth.auth", return_value={"id_token": "token"}),
        mock.patch.object(stage_module, "retrieve_dataset", return_value=dataset),
        mock.patch.object(stage_module, "FilesAPIRepo", return_value=FakeFilesAPIRepo()),
        mock.patch.object(stage_module.gpd, "read_parquet", return_value=gdf),
    ):
        stage_module.stage_dataset("my-dataset", assets=True, path=str(tmp_path / "downloads"))

    assert len(staged_urls) == 3
    assert set(staged_urls) == {
        "https://example.com/asset-1",
        "https://example.com/asset-2",
        "https://example.com/asset-3",
    }
