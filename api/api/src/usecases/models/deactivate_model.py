from ...repos import ModelsDBRepo
from ...errors import ModelDoesNotExistError, ModelNotActiveError

def deactivate_model(model_id: str):
    repo = ModelsDBRepo()
    model = repo.find_one_by_field('models','id', model_id, limit=None)
    if model is None:
        raise ModelDoesNotExistError()
    if model.get("active") is False:
        raise ModelNotActiveError()
    repo.deactivate_model(model_id)
    return f"Model {model_id} has been deactivated."