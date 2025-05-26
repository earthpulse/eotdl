from ...errors.datasets import DatasetNotActiveError
from ...repos import DatasetsDBRepo
from ...models import Dataset


def retrieve_datasets(match=None, limit=None, private=False):
    repo = DatasetsDBRepo()
    data = repo.retrieve_datasets(match, limit)
    datasets = []
    for d in data:
        # only list active and public datasets
        if (not 'active' in d or d['active']) and (not 'visibility' in d or d['visibility'] == 'public'):
            datasets.append(Dataset(**d))
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
        # only list active and public datasets
        if (not 'active' in d or d['active']) and (not 'visibility' in d or d['visibility'] == 'public'):
            datasets.append(Dataset(**d))
    return datasets


def retrieve_private_datasets(user):
    repo = DatasetsDBRepo()
    data = repo.retrieve_private_datasets(user)
    datasets = []
    for d in data:
        if not 'active' in d or d['active']:
            datasets.append(Dataset(**d))
    return datasets