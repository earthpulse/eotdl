import os
import shutil
import pytest

from pystac import Catalog

EXAMPLE_DATA_DIR = 'tests/unit/curation/stac/test_data'


@pytest.fixture
def tmp_stac_catalog():
    original_catalog_path = os.path.join(EXAMPLE_DATA_DIR, 'jaca_dataset_stac')

    os.makedirs('tmp', exist_ok=True)
    tmp_catalog_path = os.path.join('tmp', "copied_catalog")
    tmp_catalog = Catalog.from_file(os.path.join(original_catalog_path, 'catalog.json'))
    tmp_catalog.normalize_and_save(tmp_catalog_path)

    copied_catalog = Catalog.from_file(os.path.join(tmp_catalog_path, 'catalog.json'))
    yield copied_catalog
    
    shutil.rmtree('tmp')


@pytest.fixture
def tmp_stac_catalog_labels():
    original_catalog_path = os.path.join(EXAMPLE_DATA_DIR, 'jaca_dataset_stac_labels')

    os.makedirs('tmp', exist_ok=True)
    tmp_catalog_path = os.path.join('tmp', "copied_catalog")
    tmp_catalog = Catalog.from_file(os.path.join(original_catalog_path, 'catalog.json'))
    tmp_catalog.normalize_and_save(tmp_catalog_path)

    copied_catalog = Catalog.from_file(os.path.join(tmp_catalog_path, 'catalog.json'))
    yield copied_catalog
    
    shutil.rmtree('tmp')


@pytest.fixture
def tmp_stac_collection():
    original_collection_path = os.path.join(EXAMPLE_DATA_DIR, 'jaca_dataset_stac', 'collection.json')

    os.makedirs('tmp', exist_ok=True)
    tmp_collection_path = os.path.join('tmp', "copied_collection")
    shutil.copy(original_collection_path, tmp_collection_path)

    copied_collection = Catalog.from_file(os.path.join(tmp_collection_path, 'collection.json'))
    yield copied_collection
    
    shutil.rmtree('tmp')
