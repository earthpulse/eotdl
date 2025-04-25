def test_make_private_model_success(client, model, mock_mongo_model):
    response = client.patch(f"/models/{model['id']}/make-private")
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Model {model['name']} has been made private."
    }

    models_collection = mock_mongo_model.models
    model = models_collection.find_one({"id": model["id"]})
    assert model["allowed_users"] == ['123']


def test_make_private_model_already_private(client, model, mock_mongo_model):
    client.patch(f"/models/{model['id']}/make-private")

    response = client.patch(f"/models/{model['id']}/make-private")
    assert response.status_code == 409
    assert response.json() == {
        "detail": "This model is already private"
    }

    models_collection = mock_mongo_model.models
    model = models_collection.find_one({"id": model["id"]})
    assert model["allowed_users"] == ['123']


def test_make_private_model_does_not_exist(client, model, mock_mongo_model):
    response = client.patch(f"/models/234/make-private")
    assert response.status_code == 409
    assert response.json() == {
        "detail": "Model doesn't exist"
    }


def test_make_private_model_not_owner(client, model, mock_mongo_model):
    models_collection = mock_mongo_model.models
    models_collection.update_one(
        {"id": model["id"]},
        {"$set": {"uid": "other_id"}}
    )
    response = client.patch(f"/models/{model['id']}/make-private")

    assert response.status_code == 409
    assert response.json() == {
        "detail": "You are not authorized to perform this action"
    }

    models_collection = mock_mongo_model.models
    model = models_collection.find_one({"id": model["id"]})
    assert model["allowed_users"] == []

def test_allow_user_but_you_are_not_allowed(client, model, mock_mongo_model):
    models_collection = mock_mongo_model.models
    models_collection.update_one(
        {"id": model["id"]},
        {"$set": {"allowed_users": ["the_owner"]}}
    )
    response = client.patch(f"/models/{model['id']}/allow-user/456")
    assert response.status_code == 409
    assert response.json() == {
        "detail": 'You do not have access to this private dataset/model'
    }

    models_collection = mock_mongo_model.models
    model = models_collection.find_one({"id": model["id"]})
    assert model["allowed_users"] == ['the_owner']


def test_allow_user_to_private_model_success(client, model, mock_mongo_model):
    client.patch(f"/models/{model['id']}/make-private")

    response = client.patch(f"/models/{model['id']}/allow-user/456")
    assert response.status_code == 200
    assert response.json() == {
        "message": f"User 456 has been allowed to access the private model {model['name']}."
    }

    models_collection = mock_mongo_model.models
    model = models_collection.find_one({"id": model["id"]})
    assert '456' in model["allowed_users"]
