import pytest
from eotdl.hello import say_hello


def test_hello():
    assert say_hello() == "Hello, World!"
