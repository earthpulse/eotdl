import pytest
import numpy as np
import rasterio
import os
import shutil

from sentinelhub import BBox

from eotdl.tools.geo_utils import *
from shapely.geometry import box


@pytest.mark.parametrize("bbox, expected", [
    ((1, 2, 3, 4), True),
    ((-10, -20, 10, 20), True),
    ((0, 0, 100, 100), True),
    ((1, 2, 3), False), 
    ((3, 2, 1, 4), False),
    ((1, 4, 3, 2), False),
    (("a", "b", "c", "d"), False),
    ((1, 2, 3, 4, 5), False),
])
def test_is_bounding_box(bbox, expected):
    assert is_bounding_box(bbox) == expected


@pytest.mark.parametrize("input_bbox, expected_output", [
    ([1, 2, 3, 4], box(1, 2, 3, 4)),
])
def test_bbox_to_polygon(input_bbox, expected_output):
    assert bbox_to_polygon(input_bbox) == expected_output


class ParametersMock:
    RESOLUTION = 10


def test_compute_image_size():
    bounding_box = [13.35, 52.47, 13.39, 52.5]
    parameters = ParametersMock()

    bbox, bbox_size = compute_image_size(bounding_box, parameters)

    assert isinstance(bbox, BBox)
    assert isinstance(bbox_size, tuple)
    assert len(bbox_size) == 2
    assert bbox_size == (279, 328)


@pytest.fixture
def mock_raster():
    os.makedirs("tmp", exist_ok=True)
    raster_path = "tmp/mock_raster.tif"

    data = np.random.rand(100, 100).astype('float32')

    with rasterio.open(
        raster_path,
        'w',
        driver='GTiff',
        height=data.shape[0],
        width=data.shape[1],
        count=1,
        dtype=data.dtype,
        crs='+proj=latlong',
        transform=rasterio.transform.from_origin(1, 1, 0.05, 0.05),
    ) as dst:
        dst.write(data, 1)

    yield raster_path
    shutil.rmtree("tmp")


def test_get_image_bbox(mock_raster):
    bbox = get_image_bbox(mock_raster)
    assert isinstance(bbox, list)
    assert len(bbox) == 4


def test_get_image_resolution(mock_raster):
    resolution = get_image_resolution(mock_raster)
    assert isinstance(resolution, tuple)
    assert resolution == (0.05, 0.05)
