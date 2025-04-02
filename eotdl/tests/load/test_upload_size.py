from datetime import datetime, timezone
import io
import os
from pathlib import Path
import tempfile
import time

from eotdl.datasets.retrieve import retrieve_dataset_files
import numpy as np
import pytest

from eotdl.datasets import ingest_dataset, retrieve_dataset
import rasterio


os.environ["EOTDL_API_URL"] = "http://localhost:8000/"


def write_readme(path: Path, name: str):
    readme_text = f"""---
name: {name}
authors: 
  - Derek van de Ven
license: free
source: https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/02_ingesting.ipynb
---

# {name}

This file is nonsensical data used for load testing. It should not be stored on the web. 
"""

    with open(path / name / "README.md", "w") as outfile:
        outfile.write(readme_text)


def generate_fake_tif_dataset(
    path: Path, n_tifs: int = 10, tif_size: int = 256, name: str = "test_set"
):
    files_to_upload = []
    for count in range(n_tifs):
        files_to_upload.append(f"{name}/FakeFolder/Fake_tif{count}.tif")

    for rel_path in files_to_upload:
        file_path = path / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)

        width, height = tif_size, tif_size
        data = np.full((height, width, 3), 256, dtype=np.uint32)

        with rasterio.open(
            file_path,
            "w",
            driver="GTiff",
            height=height,
            width=width,
            count=3,
            dtype="uint32",
            crs="EPSG:4326",
            transform=rasterio.transform.from_origin(0, height, 1, 1),
        ) as dst:
            dst.write(data[:, :, 0], 1)
            dst.write(data[:, :, 1], 2)
            dst.write(data[:, :, 2], 3)

    write_readme(path, name)


def generate_fake_dataset(
    path: Path, size_mb: int = 10, n_files: int = 5, name: str = "test_set"
):
    files_to_upload = []
    for count in range(n_files):
        files_to_upload.append(
            f"{name}/FakeFolder/Fake_tif{count}.tif",
        )

    total_size_bytes = size_mb * 1024 * 1024
    file_size = total_size_bytes // len(files_to_upload)

    for rel_path in files_to_upload:
        file_path = path / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write random binary data to simulate `.tif` files
        with open(file_path, "wb") as f:
            f.write(os.urandom(file_size))  # Random binary data

    write_readme(path, name)


@pytest.mark.parametrize(
    "total_size, n_files",
    [
        (1, 10),
        # (1e1, 10),
        # (1e3, 1), # 1 files amounting to 1 GB,
        # (1e3, 20), # 20 files amounting to 1 GB
        # (1e4, 100), # 100 10 MB files
        # (3e4, 100), # 10 times 1 GB
    ],
)
def test_load(setup_mongo, setup_minio, total_size, n_files):
    name = f"LoadTest-{int(total_size)}MB"
    with tempfile.TemporaryDirectory(prefix="loadtest_") as tmpdir:
        tmpdir = Path(tmpdir)
        generate_fake_dataset(
            path=tmpdir, size_mb=int(total_size), n_files=n_files, name=name
        )

        # upload
        start_time = time.time()
        ingest_dataset(path=str(tmpdir / name))

        upload_duration = time.time() - start_time
        print(f"Upload for {name} took {upload_duration:.2f} seconds.")

        with open("eotdl/tests/load/upload_times.log", "a") as log_file:
            log_file.write(
                f"{total_size} MB made of {n_files} files took {upload_duration:.2f} seconds.\n"
            )

        # assert dataset ingested
        dataset = retrieve_dataset(name=name)
        assert dataset["name"] == name
        assert round(dataset["versions"][0]["size"] / (1024 * 1024), 2) == total_size

        # check files in minio
        minio_files = []
        minio_sizes = []
        for obj in setup_minio.list_objects("eotdl-test", recursive=True):
            minio_files.append(obj.object_name)
            minio_sizes.append(obj.size)
            assert obj.object_name.endswith(("tif", "md", "parquet"))

        assert len(minio_files) == n_files + 2
        assert round(sum(minio_sizes) / (1024 * 1024)) == total_size


@pytest.mark.parametrize(
    "tif_size, n_tifs",
    [
        # (256, 100),
        # (512, 100),
        # (1024, 100),
        (2048, 200),
    ],
)
def test_load_tifs(setup_mongo, setup_minio, tif_size, n_tifs):
    name = f"LoadTest-{int(tif_size)}"
    with tempfile.TemporaryDirectory(prefix="loadtest_") as tmpdir:
        tmpdir = Path(tmpdir)
        generate_fake_tif_dataset(
            path=tmpdir, tif_size=tif_size, n_tifs=n_tifs, name=name
        )

        # upload
        start_time = time.time()
        ingest_dataset(path=str(tmpdir / name))

        upload_duration = time.time() - start_time
        print(f"Upload for {name} took {upload_duration:.2f} seconds.")

        # assert dataset ingested
        dataset = retrieve_dataset(name=name)
        assert dataset["name"] == name

        with open("eotdl/tests/load/upload_times_tifs.log", "a") as log_file:
            log_file.write(
                f"{tif_size}x {tif_size} made of {n_tifs} files took {upload_duration:.2f} seconds. ({round(dataset['versions'][0]['size'] / (1024 * 1024), 2)} mb)\n"
            )

        # check files in minio
        minio_files = []
        minio_sizes = []
        for obj in setup_minio.list_objects("eotdl-test", recursive=True):
            minio_files.append(obj.object_name)
            minio_sizes.append(obj.size)
            assert obj.object_name.endswith(("tif", "md", "parquet"))

            if obj.object_name.endswith(".tif"):
                file = setup_minio.get_object("eotdl-test", obj.object_name)
                file_content = file.read()
                with io.BytesIO(file_content) as byte_file:
                    with rasterio.open(byte_file) as src:
                        assert src.crs == "EPSG:4326"
                        assert src.width == src.height == tif_size
                        assert src.dtypes == ("uint32", "uint32", "uint32")

                        for band in range(1, 4):
                            colour = src.read(band)
                            assert set(colour.flatten()) == {np.uint32(256)}

        assert len(minio_files) == n_tifs + 2
