from ...repos import ModelsDBRepo
from ...errors import ModelDoesNotExistError, ModelNotActiveError
from .retrieve_model import retrieve_owned_model

def deactivate_model(model_id, user):
    model = retrieve_owned_model(model_id, user.uid)
    repo = ModelsDBRepo()
    repo.deactivate_model(model_id)
    return f"Model {model_id} has been deactivated."