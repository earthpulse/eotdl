from fastapi.testclient import TestClient
from api.main import app


client = TestClient(app)


def test_deactivate_model_success(model, mock_mongo_model):
    response = client.patch(f"/models/deactivate/{model['id']}")
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Model {model['id']} has been deactivated."
    }

    models_collection = mock_mongo_model.models
    model = models_collection.find_one({"id": model["id"]})
    assert model["active"] == False


def test_deactivate_model_does_not_exist():
    response = client.patch("/models/deactivate/non_existent_model")
    assert response.status_code == 409
    assert response.json() == {"detail": "Model doesn't exist"}


def test_deactivate_model_already_deactivated(model, mock_mongo_model):
    client.patch(f"/models/deactivate/{model['id']}")
    models_collection = mock_mongo_model.models
    model = models_collection.find_one({"id": model["id"]})
    assert model["active"] == False
