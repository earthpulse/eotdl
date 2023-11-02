import pytest
import os
import json
from eotdl.tools import get_item_metadata, remove_raster_metadata


# Create a fixture for a temporary directory and sample files
@pytest.fixture
def temp_dir(tmpdir):
    raster_file = tmpdir.join("sample.tif")
    metadata_file = tmpdir.join("metadata.json")
    same_name_metadata_file = tmpdir.join("sample.json")
    
    # Create a sample metadata content
    metadata_content = {"sample_key": "sample_value"}

    with open(metadata_file, 'w') as f:
        json.dump(metadata_content, f)
        
    with open(same_name_metadata_file, 'w') as f:
        json.dump(metadata_content, f)
    
    return str(tmpdir), str(raster_file)


def test_get_item_metadata(temp_dir):
    dir_path, raster_path = temp_dir
    metadata = get_item_metadata(raster_path)
    
    assert metadata is not None
    assert metadata["sample_key"] == "sample_value"

    # Additional tests can be to delete the 'metadata.json' and ensure the code picks up 'sample.json'
    os.remove(os.path.join(dir_path, 'metadata.json'))
    metadata = get_item_metadata(raster_path)
    assert metadata is not None

    # Further, you can remove 'sample.json' and ensure the function returns None
    os.remove(os.path.join(dir_path, 'sample.json'))
    assert get_item_metadata(raster_path) is None


def test_remove_raster_metadata(temp_dir):
    dir_path, _ = temp_dir
    remove_raster_metadata(dir_path)
    remove_raster_metadata(dir_path, 'sample.json')
    
    # Assert that the metadata files are removed
    assert not os.path.exists(os.path.join(dir_path, 'metadata.json'))
    assert not os.path.exists(os.path.join(dir_path, 'sample.json'))
