from fastapi.testclient import TestClient
from api.main import app


client = TestClient(app)

# tests to make sure stac api conforms to core conformance class

def test_stac_core_conformation():

    response = client.get("/")
    assert "links" in response.keys()
    assert "conformsTo" in response.keys()

# returns stac catalog

# has links attribute providing links to api endpoints

# has conformsTo attribute providing