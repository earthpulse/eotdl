import pytest

from eotdl.tools.geo_utils import is_bounding_box, bbox_to_polygon
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
