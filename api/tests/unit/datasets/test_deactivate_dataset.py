from fastapi.testclient import TestClient
from api.main import app


client = TestClient(app)


def test_deactivate_dataset_success(dataset, mock_mongo):
    response = client.patch(f"/datasets/deactivate/{dataset['id']}")
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Dataset {dataset['id']} has been deactivated."
    }

    datasets_collection = mock_mongo.datasets
    dataset = datasets_collection.find_one({"id": dataset["id"]})
    assert dataset["active"] == False


def test_deactivate_dataset_does_not_exist():
    response = client.patch("/datasets/deactivate/non_existent_dataset")
    assert response.status_code == 409
    assert response.json() == {"detail": "Dataset doesn't exist"}


def test_deactivate_dataset_already_deactivated(dataset, mock_mongo):
    client.patch(f"/datasets/deactivate/{dataset['id']}")
    datasets_collection = mock_mongo.datasets
    dataset = datasets_collection.find_one({"id": dataset["id"]})
    assert dataset["active"] == False

    response2 = client.patch(f"/datasets/deactivate/{dataset['id']}")
    assert response2.status_code == 409
    assert response2.json() == {"detail": "Requested dataset(s) not active"}
