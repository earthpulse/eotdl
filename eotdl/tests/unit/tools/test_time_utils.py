import pytest
from datetime import datetime

from eotdl.tools.time_utils import is_time_interval, create_time_slots, is_valid_date, get_day_between


@pytest.mark.parametrize("input_time_interval, expected_output", [
    (["2022-01-01", "2022-01-10"], True),
    (["2021-05-15", "2021-05-16"], True),
    ([], False),
    (["2022-01-01"], False),
    (["2022-01-01", "2022-01-10", "2022-01-11"], False),
    ([2022, 1], False),
    ("2022-01-01,2022-01-10", False),
    (["08:00", "18:00"], False),
    (["2022-01-32", "2022-01-10"], False),
])
def test_is_time_interval(input_time_interval, expected_output):
    assert is_time_interval(input_time_interval) == expected_output


@pytest.mark.parametrize("start_date, end_date, n_chunks, expected_output", [
    (
        datetime(2022, 1, 1),
        datetime(2022, 1, 3),
        3,
        [('2022-01-01', '2022-01-01'), ('2022-01-01', '2022-01-02')]
    ),
    (
        datetime(2022, 1, 1),
        datetime(2022, 1, 6),
        3,
        [('2022-01-01', '2022-01-02'), ('2022-01-02', '2022-01-04')]
    )
])
def test_create_time_slots(start_date, end_date, n_chunks, expected_output):
    assert create_time_slots(start_date, end_date, n_chunks) == expected_output


@pytest.mark.parametrize("input_date, expected_output", [
    ("2022-01-01", True),
    ("2000-02-29", True),
    ("2022-01-32", False),
    ("2022-13-01", False),
    ("2022-02-30", False),
    ("2001-02-29", False),
    ("22-01-01", False), 
    ("", False), 
    ("NotADate", False),
])

def test_is_valid_date(input_date, expected_output):
    assert is_valid_date(input_date) == expected_output

@pytest.mark.parametrize(
    "from_date, to_date, expected", 
    [
        ("2019-12-31T00:00:00Z", "2020-01-02T23:59:59Z", "2020-01-01"),
        (datetime(2019, 12, 31, 0, 0), datetime(2020, 1, 2, 23, 59, 59), "2020-01-01"),
        ("2020-01-01T00:00:00Z", "2020-01-03T23:59:59Z", "2020-01-02"),
        (datetime(2020, 1, 1, 0, 0), datetime(2020, 1, 3, 23, 59, 59), "2020-01-02"),
    ]
)
def test_get_day_between(from_date, to_date, expected):
    assert get_day_between(from_date, to_date) == expected
