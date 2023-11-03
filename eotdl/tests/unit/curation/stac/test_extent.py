import pytest
import pystac
from datetime import datetime

from eotdl.curation.stac.extent import (
    get_dem_temporal_interval,
    get_unknow_temporal_interval,
    get_unknow_extent,
)


def test_get_dem_temporal_interval():
    expected_interval = [(datetime(2011, 1, 1, 0, 0), datetime(2015, 1, 7, 0, 0))]
    result_interval = get_dem_temporal_interval()
    assert result_interval.intervals == expected_interval


def test_get_unknow_temporal_interval():
    expected_interval = [(datetime(2000, 1, 1, 0, 0), datetime(2023, 12, 31, 0, 0))]
    result_interval = get_unknow_temporal_interval()
    assert result_interval.intervals == expected_interval


def test_get_unknow_extent():
    expected_spatial_extent = [[0, 0, 0, 0]]
    expected_temporal_extent = [
        (datetime(2000, 1, 1, 0, 0), datetime(2023, 12, 31, 0, 0))
    ]

    result_interval = get_unknow_extent()

    assert result_interval.spatial.bboxes == expected_spatial_extent
    assert result_interval.temporal.intervals == expected_temporal_extent
