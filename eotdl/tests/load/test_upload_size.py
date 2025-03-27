from datetime import datetime, timezone
import os
from pathlib import Path
import tempfile
import time

import pytest

from eotdl.datasets import ingest_dataset, retrieve_dataset


os.environ["EOTDL_API_URL"] = "http://localhost:8000/"


def generate_fake_dataset(path: Path, size_mb: int = 10, n_files: int = 5, name: str = "test_set"):
    
    files_to_upload = []
    for count in range(n_files):
        files_to_upload.append(f"{name}/FakeFolder/Fake_tif{count}.tif",)

    total_size_bytes = size_mb * 1024 * 1024
    file_size = total_size_bytes // len(files_to_upload)

    for rel_path in files_to_upload:
        file_path = path / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write random binary data to simulate `.tif` files
        with open(file_path, "wb") as f:
            f.write(os.urandom(file_size))  # Random binary data

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


@pytest.mark.parametrize(
    "total_size, n_files",
    [
        (1, 10),
        (1e1, 10),
        (1e2, 10),
        (1e3, 20), # 1GB
        # (1e4, 1),
        # (1e5, 1),
        # (1e6, 1)  # 1TB 
    ],
)
def test_load(setup_mongo, total_size, n_files):
    name = f"LoadTest-{int(total_size)}MB"
    with tempfile.TemporaryDirectory(prefix="loadtest_") as tmpdir:
        tmpdir = Path(tmpdir)
        generate_fake_dataset(path=tmpdir, size_mb=int(total_size), n_files=n_files, name=name)

        # upload
        start_time = time.time()
        ingest_dataset(path=str(tmpdir / name))

        upload_duration = time.time() - start_time
        print(f"Upload for {name} took {upload_duration:.2f} seconds.")

        with open("eotdl/tests/load/upload_times.log", "a") as log_file:
            log_file.write(f"{total_size} MB made of {n_files} files took {upload_duration:.2f} seconds.\n")

        # assert dataset ingested
        dataset = retrieve_dataset(name=name)
        assert dataset["name"] == name
