from ...repos import PipelinesDBRepo
from ...models import Pipeline
from ...errors import PipelineNotActiveError


def retrieve_pipelines(match=None, limit=None):
    repo = PipelinesDBRepo()
    data = repo.retrieve_pipelines(match, limit)
    models = []
    for d in data:
        if not 'active' in d or d['active']:
            models.append(Pipeline(**d))
    if not models:
        raise PipelineNotActiveError()
    return models
    


def retrieve_pipelines_leaderboard():
    repo = PipelinesDBRepo()
    users = repo.retrieve_pipelines_leaderboard()
    leaderboard = [
        {"name": user["name"], "pipelines": user["pipelines_count"]} for user in users
    ]
    return leaderboard


def retrieve_popular_pipelines(limit):
    repo = PipelinesDBRepo()
    data = repo.retrieve_popular_pipelines(limit)
    models = []
    for d in data:
        models.append(Pipeline(**d))
    return models
