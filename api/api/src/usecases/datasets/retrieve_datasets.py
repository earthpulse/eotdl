from ...errors.datasets import DatasetNotActiveError
from ...repos import DatasetsDBRepo
from ...models import Dataset


def retrieve_datasets(match=None, limit=None):
    repo = DatasetsDBRepo()
    data = repo.retrieve_datasets(match, limit)
    datasets = []
    for d in data:
        datasets.append(Dataset(**d))
    if not datasets:
        raise DatasetNotActiveError()
    return datasets


def retrieve_datasets_leaderboard():
    repo = DatasetsDBRepo()
    users = repo.retrieve_datasets_leaderboard()
    leaderboard = [
        {"name": user["name"], "datasets": user["dataset_count"]} for user in users
    ]
    return leaderboard


def retrieve_popular_datasets(limit):
    repo = DatasetsDBRepo()
    data = repo.retrieve_popular_datasets(limit)
    datasets = []
    for d in data:
        datasets.append(Dataset(**d))
    return datasets
