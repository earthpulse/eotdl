import pytest
import numpy as np
import rasterio
import os
import shutil
import pandas as pd

from sentinelhub import BBox

from eotdl.tools.geo_utils import *
from shapely.geometry import box, Point


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


def test_bbox_to_coordinates():
    bbox = [1, 2, 3, 4]
    coordinates = bbox_to_coordinates(bbox)
    assert isinstance(coordinates, list)
    assert len(coordinates) == 5
    assert coordinates == [(1, 2), (1, 4), (3, 4), (3, 2), (1, 2)]


def test_bbox_to_polygon():
    bbox = [1, 2, 3, 4]
    polygon = bbox_to_polygon(bbox)
    assert isinstance(polygon, Polygon)
    assert polygon.bounds == (1, 2, 3, 4)


def test_bbox_from_centroid():
    bbox = bbox_from_centroid(0, 0, 10, 2, 2)
    assert isinstance(bbox, list)
    assert len(bbox) == 4
    bbox_round = [round(i, 4) for i in bbox]
    assert bbox_round == [-0.0001, -0.0001, 0.0001, 0.0001]


def test_generate_bounding_box():
    point = Point(0, 0)
    differences = [2, 2]

    bbox = generate_bounding_box(point, differences)
    expected_bbox = [-1, -1, 1, 1]

    assert bbox == expected_bbox


def test_convert_df_geom_to_shape():
    data = {'geometry': [Point(0, 0).__geo_interface__]}
    df = pd.DataFrame(data)

    row_with_geom = df.iloc[0]
    result_wkt_with_geom = convert_df_geom_to_shape(row_with_geom)

    assert result_wkt_with_geom == "POINT (0 0)"

    row_without_geom = pd.Series({"geometry": None})
    result_wkt_without_geom = convert_df_geom_to_shape(row_without_geom)

    assert result_wkt_without_geom == "POLYGON EMPTY"
