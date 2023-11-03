import pytest
try:
    from lib.eotdl import SHClient
except ImportError:
    from eotdl import SHClient


def test_sh_client():
    client = SHClient(sh_client_id='my_client_id',
    sh_client_secret='my_client_secret')

    assert client.config.sh_client_id is not None


def test_search_available_sentinel_data():
    pass


def test_request_bulk_data():
    pass


def test_request_data():
    pass
