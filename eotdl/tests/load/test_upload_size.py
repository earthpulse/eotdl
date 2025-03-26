import os
from pathlib import Path
import tempfile

from eotdl.eotdl.datasets import ingest_dataset, retrieve_dataset

# from api.api.src.usecases.datasets.delete_dataset import delete_dataset




def generate_fake_dataset(path: Path, size_mb: int = 10, name: str = "test_set"):
    files_to_upload = [
        f"{name}/Forest/Fake_tif1.tif",
        f"{name}/Forest/Fake_tif2.tif",
        f"{name}/AnnualCrop/Fake_tif1.tif",
        f"{name}/AnnualCrop/Fake_tif2.tif",
    ]

    total_size_bytes = size_mb * 1024 * 1024
    file_size = total_size_bytes // len(files_to_upload)

    for rel_path in files_to_upload:
        file_path = path / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write random binary data to simulate `.tif` files
        with open(file_path, "wb") as f:
            f.write(os.urandom(file_size))  # Random binary data

    # Write README file
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


def test_load_10mb(load_tiers):

    name = "LoadTest"
    with tempfile.TemporaryDirectory(prefix="loadtest_") as tmpdir:
        tmpdir = Path(tmpdir)
        generate_fake_dataset(path=tmpdir, size_mb=10, name=name)

        # upload
        ingest_dataset(path=str(tmpdir / name))

        # check if it worked
        assert retrieve_dataset(name=name)

        # delete
        # delete_dataset(name=name)

        # check dataset is gone
        # assert not retrieve_dataset(name=name)
