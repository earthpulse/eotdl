from fastapi.testclient import TestClient
from api.api.main import app


client = TestClient(app)

# tests to make sure stac api conforms to core conformance class

def test_stac_core_conformation():

    response = client.get("stac/")
    core = response.json()
    assert response.status_code == 200
    assert "links" in core.keys()
    assert "conformsTo" in core.keys()

    assert "type" in core.keys()
    assert "stac_version" in core.keys()
    assert "id" in core.keys()
    assert "description" in core.keys()

    assert core["type"] == "Catalog"


def test_stac_api_conformation():
    response = client.get("stac/api")
    assert response.status_code == 200
    assert response.json()