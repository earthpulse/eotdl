def test_deactivate_model_success(client, model, mock_mongo_model):
    response = client.patch(f"/models/{model['id']}/deactivate")
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Model {model['id']} has been deactivated."
    }

    models_collection = mock_mongo_model.models
    model = models_collection.find_one({"id": model["id"]})
    assert model["active"] == False


def test_deactivate_model_does_not_exist(client):
    response = client.patch("/models/non_existent_model/deactivate")
    assert response.status_code == 409
    assert response.json() == {"detail": "Model doesn't exist"}


def test_deactivate_model_already_deactivated(client, model, mock_mongo_model):
    response = client.patch(f"/models/{model['id']}/deactivate")
    assert response.status_code == 200
    
    models_collection = mock_mongo_model.models
    model = models_collection.find_one({"id": model["id"]})
    assert model["active"] == False

    response2 = client.patch(f"/models/{model['id']}/deactivate")
    assert response2.status_code == 409
    assert response2.json() == {"detail": "Requested model(s) not active"}
