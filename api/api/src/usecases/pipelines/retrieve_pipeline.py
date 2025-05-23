from ...models import Pipeline
from ...errors import PipelineDoesNotExistError, UserUnauthorizedError, PipelineNotActiveError
from ...repos import PipelinesDBRepo


def retrieve(data):
    if data is None:
        raise PipelineDoesNotExistError()
    if 'active' in data and data['active'] is False:
        raise PipelineNotActiveError()
    return Pipeline(**data)


def retrieve_pipeline(pipeline_id):
    repo = PipelinesDBRepo()
    data = repo.retrieve_pipeline(pipeline_id)
    return retrieve(data)


def retrieve_pipeline_by_name(name):
    repo = PipelinesDBRepo()
    data = repo.find_one_pipeline_by_name(name)
    return retrieve(data)


def retrieve_owned_pipeline(pipeline_id, uid):
    model = retrieve_pipeline(pipeline_id)
    if model.uid != uid:
        raise UserUnauthorizedError()
    return model