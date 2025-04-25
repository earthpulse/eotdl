def test_deactivate_dataset_success(client, dataset, mock_mongo_datasets):
    response = client.patch(f"/datasets/{dataset['id']}/deactivate", )
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Dataset {dataset['name']} has been deactivated."
    }

    datasets_collection = mock_mongo_datasets.datasets
    dataset = datasets_collection.find_one({"id": dataset["id"]})
    assert dataset["active"] == False


def test_deactivate_dataset_does_not_exist(client):
    response = client.patch("/datasets/non_existent_dataset/deactivate")
    assert response.status_code == 409
    assert response.json() == {"detail": "Dataset doesn't exist"}


def test_deactivate_dataset_already_deactivated(client, dataset, mock_mongo_datasets):
    response = client.patch(f"/datasets/{dataset['id']}/deactivate")
    assert response.status_code == 200

    datasets_collection = mock_mongo_datasets.datasets
    dataset = datasets_collection.find_one({"id": dataset["id"]})
    assert dataset["active"] == False

    response2 = client.patch(f"/datasets/{dataset['id']}/deactivate")
    assert response2.status_code == 409
    assert response2.json() == {"detail": "Requested dataset(s) not active"}
