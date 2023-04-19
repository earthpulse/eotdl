import pytest
from eotdl import EOTDLClient


def test_eotdl_client():
    client = EOTDLClient(sh_client_id='2fdc33ba-43dd-4044-bcdf-e351f13befb6', 
                     sh_client_secret='R2*pJLtWRW+KK+zSQj&vS8^0-NE&}-_so&r2t2Bo')
    
    assert client.sh_client_id is not None
