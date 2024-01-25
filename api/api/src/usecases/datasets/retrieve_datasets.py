from ...repos import DatasetsDBRepo
from ...models import Dataset, STACDataset


def retrieve_datasets(match=None, limit=None):
    repo = DatasetsDBRepo()
    data = repo.retrieve_datasets(match, limit)
    datasets = []
    for d in data:
        if d["quality"] == 0:
            datasets.append(Dataset(**d))
        else:
            datasets.append(STACDataset(**d))
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
        if d["quality"] == 0:
            datasets.append(Dataset(**d))
        else:
            datasets.append(STACDataset(**d))
    return datasets
