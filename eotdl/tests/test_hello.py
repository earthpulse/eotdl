import pytest 
try:
    from lib.eotdl import say_hello
except ImportError:
    from eotdl import say_hello

def test_hello():
    assert say_hello() == "Hello, World!"