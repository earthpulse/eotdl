from ...repos import ModelsDBRepo
from ...models import Model, STACModel


def retrieve_models(match=None, limit=None):
    repo = ModelsDBRepo()
    data = repo.retrieve_models(match, limit)
    models = []
    for d in data:
        if d["quality"] == 0:
            models.append(Model(**d))
        else:
            models.append(STACModel(**d))
    return models


def retrieve_models_leaderboard():
    repo = ModelsDBRepo()
    users = repo.retrieve_models_leaderboard()
    leaderboard = [
        {"name": user["name"], "models": user["models_count"]} for user in users
    ]
    return leaderboard


def retrieve_popular_models(limit):
    repo = ModelsDBRepo()
    data = repo.retrieve_popular_models(limit)
    models = []
    for d in data:
        if d["quality"] == 0:
            models.append(Model(**d))
        else:
            models.append(STACModel(**d))
    return models
