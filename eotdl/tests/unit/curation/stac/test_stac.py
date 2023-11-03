import os
import requests

import pytest
import pystac

from jsonschema import validate, RefResolver

from .fixtures import tmp_sentinel_2, sentinel_2

from eotdl.curation.stac.stac import STACGenerator
from eotdl.curation.stac.assets import STACAssetGenerator, BandsAssetGenerator
from eotdl.curation.stac.parsers import UnestructuredParser
from eotdl.curation.stac.dataframe_labeling import LabeledStrategy, UnlabeledStrategy

CATALOG_SCHEMA_URL = 'https://github.com/radiantearth/stac-spec/blob/master/catalog-spec/json-schema/catalog.json'
COLLECTION_SCHEMA_URL = 'https://github.com/radiantearth/stac-spec/blob/master/collection-spec/json-schema/collection.json'


@pytest.mark.parametrize("labeling_strategy", [
    (LabeledStrategy),
    (UnlabeledStrategy)
])
def test_stac_generation_labeling(labeling_strategy, sentinel_2):
    stac_generator = STACGenerator(item_parser=UnestructuredParser, 
                                   assets_generator=STACAssetGenerator, 
                                   labeling_strategy=labeling_strategy,
                                   image_format='tif'
                                   )
    df = stac_generator.get_stac_dataframe(sentinel_2)
    stac_generator.generate_stac_metadata(stac_id='test-dataset',
                                          description='Test dataset',
                                          output_folder='tmp/sentinel_2_stac')
    
    assert_paths_exists('tmp/sentinel_2_stac')
    
    catalog = pystac.Catalog.from_file('tmp/sentinel_2_stac/catalog.json')
    collection = pystac.Collection.from_file('tmp/sentinel_2_stac/source/collection.json')
    assert_catalog_collection_schema(catalog, collection)


def test_stac_generation_bands(tmp_sentinel_2):
    stac_generator = STACGenerator(item_parser=UnestructuredParser, 
                                   assets_generator=BandsAssetGenerator, 
                                   labeling_strategy=LabeledStrategy,
                                   image_format='tif'
                                   )
    bands = {'Boadella': ['B02', 'B03', 'B04'],}
    df = stac_generator.get_stac_dataframe(tmp_sentinel_2, bands=bands)
    stac_generator.generate_stac_metadata(stac_id='test-dataset',
                                          description='Test dataset',
                                          output_folder='tmp/sentinel_2_stac')
    
    assert_paths_exists('tmp/sentinel_2_stac')

    catalog = pystac.Catalog.from_file('tmp/sentinel_2_stac/catalog.json')
    collection = pystac.Collection.from_file('tmp/sentinel_2_stac/source/collection.json')
    assert_catalog_collection_schema(catalog, collection)

    assert len(os.listdir(tmp_sentinel_2)) == 10

    items = collection.get_all_items()
    for i in items:
        assets = i.to_dict()["assets"]
        assert len(assets) == 3


def assert_paths_exists(dir: str):
    """
    Assert that all the paths in the directory exist
    """
    assert os.path.exists(f'{dir}/catalog.json')
    assert os.path.exists(f'{dir}/source/collection.json')
    assert len(os.listdir(f'{dir}/source')) == 3


def assert_catalog_collection_schema(catalog: pystac.Catalog, collection: pystac.Collection):
    """
    Assert that the catalog and collection are valid against the schema
    """
    schema = requests.get(CATALOG_SCHEMA_URL).json()
    resolver = RefResolver(base_uri=CATALOG_SCHEMA_URL, referrer=schema)
    
    assert validate(instance=catalog.to_dict(), schema=schema, resolver=resolver) is None

    schema = requests.get(COLLECTION_SCHEMA_URL).json()
    resolver = RefResolver(base_uri=COLLECTION_SCHEMA_URL, referrer=schema)

    assert validate(instance=collection.to_dict(), schema=schema, resolver=resolver) is None
