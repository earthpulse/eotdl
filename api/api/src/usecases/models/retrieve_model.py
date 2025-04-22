from ...models import Model
from ...errors import ModelDoesNotExistError, UserUnauthorizedError, ModelNotActiveError
from ...repos import ModelsDBRepo


def retrieve(data):
    if data is None:
        raise ModelDoesNotExistError()
    if 'active' in data and data['active'] is False:
        raise ModelNotActiveError()
    return Model(**data)


def retrieve_model(model_id):
    repo = ModelsDBRepo()
    data = repo.retrieve_model(model_id)
    return retrieve(data)


def retrieve_model_by_name(name):
    repo = ModelsDBRepo()
    data = repo.find_one_model_by_name(name)
    return retrieve(data)


def retrieve_owned_model(model_id, uid):
    model = retrieve_model(model_id)
    if model.uid != uid:
        raise UserUnauthorizedError()
    return model