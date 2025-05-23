def test_make_private_dataset_success(client, dataset, mock_mongo_dataset):
    response = client.patch(f"/datasets/{dataset['id']}/make-private")
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Dataset {dataset['name']} has been made private."
    }

    datasets_collection = mock_mongo_dataset.datasets
    dataset = datasets_collection.find_one({"id": dataset["id"]})
    assert dataset["allowed_users"] == ['123']


def test_make_private_dataset_already_private(client, dataset, mock_mongo_dataset):
    client.patch(f"/datasets/{dataset['id']}/make-private")

    response = client.patch(f"/datasets/{dataset['id']}/make-private")
    assert response.status_code == 409
    assert response.json() == {
        "detail": "This dataset is already private"
    }

    datasets_collection = mock_mongo_dataset.datasets
    dataset = datasets_collection.find_one({"id": dataset["id"]})
    assert dataset["allowed_users"] == ['123']


def test_make_private_dataset_does_not_exist(client, dataset, mock_mongo_dataset):
    response = client.patch(f"/datasets/234/make-private")
    assert response.status_code == 409
    assert response.json() == {
        "detail": "Dataset doesn't exist"
    }


def test_make_private_dataset_not_owner(client, dataset, mock_mongo_dataset):
    datasets_collection = mock_mongo_dataset.datasets
    datasets_collection.update_one(
        {"id": dataset["id"]},
        {"$set": {"uid": "other_id"}}
    )
    response = client.patch(f"/datasets/{dataset['id']}/make-private")

    assert response.status_code == 409
    assert response.json() == {
        "detail": "You are not authorized to perform this action"
    }

    dataset = datasets_collection.find_one({"id": dataset["id"]})
    assert dataset["allowed_users"] == []


def test_allow_user_but_you_are_not_allowed(client, dataset, mock_mongo_dataset):
    datasets_collection = mock_mongo_dataset.datasets
    datasets_collection.update_one(
        {"id": dataset["id"]},
        {"$set": {"allowed_users": ["the_owner"]}}
    )
    response = client.patch(f"/datasets/{dataset['id']}/allow-user/456")
    assert response.status_code == 409
    assert response.json() == {
        "detail": 'You do not have access to this private dataset/model'
    }

    dataset = datasets_collection.find_one({"id": dataset["id"]})
    assert dataset["allowed_users"] == ['the_owner']


def test_allow_user_to_private_dataset_success(client, dataset, mock_mongo_dataset):
    client.patch(f"/datasets/{dataset['id']}/make-private")

    response = client.patch(f"/datasets/{dataset['id']}/allow-user/456")
    assert response.status_code == 200
    assert response.json() == {
        "message": f"User 456 has been allowed to access the private dataset {dataset['name']}."
    }

    datasets_collection = mock_mongo_dataset.datasets
    dataset = datasets_collection.find_one({"id": dataset["id"]})
    assert '456' in dataset["allowed_users"]
