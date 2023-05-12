import pytest
try:
    from lib.eotdl import format_time_acquired
except ImportError:
    from eotdl import format_time_acquired


# test format_time_acquired
@pytest.mark.parametrize(
    "dt, expected",
    [
        ("2021-01-01", "2021-01-01T00:00:00.000000"),
        ("2021-01-01", "2021-01-01T00:00:00.000000"),
        ("2021-01-01", "2021-01-01T00:00:00.000000"),
        ("2021-01-01", "2021-01-01T00:00:00.000000"),
        ("2021-01-01", "2021-01-01T00:00:00.000000"),
        ("2021-01-01", "2021-01-01T00:00:00.000000"),
        ("2021-01-01", "2021-01-01T00:00:00.000000"),
        ("2021-01-01", "2021-01-01T00:00:00.000000"),
        ("2021-01-01", "2021-01-01T00:00:00.000000"),
    ],
)
def test_format_time_acquired(dt, expected):
    assert format_time_acquired(dt) == expected
