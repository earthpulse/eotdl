from datetime import datetime

from ...repos import ModelsDBRepo
from .retrieve_model import retrieve_model, retrieve_model_by_name
from ...errors import ModelAlreadyExistsError, ModelDoesNotExistError
from ...models import Model, ChangeType, NotificationType
from ..notifications import create_notification
from ..changes import create_change
from ..user import retrieve_user
def update_model(
    model_id, user, model
):
    _model = retrieve_model(model_id)
    if user.uid != _model.uid:
        # user is not the owner of the model, so any change should be approved by the owner or moderators
        return propose_model_update(_model.name, user, model)
    
    # update name
    if model.name != _model.name:
        try:
            __model = retrieve_model_by_name(model.name)
            if __model.id != model_id:
                raise ModelAlreadyExistsError()
        except ModelDoesNotExistError:
            pass

    # # validate tags
    # if tags:
    #     tags_data = repo.retrieve_tags()
    #     all_tags = [tag["name"] for tag in tags_data]
    #     for tag in tags:
    #         if tag not in all_tags:
    #             raise InvalidTagError()

    # update dataset
    _model.name = model.name
    _model.metadata = model.metadata
    _model.updatedAt = datetime.now()
    # update model in db
    repo = ModelsDBRepo()
    repo.update_model(model_id, _model.model_dump())
    return _model

def propose_model_update(model_name, user, model):
    change = create_change(
        user,
        ChangeType.MODEL_UPDATE,
        model,
    )
    create_notification(
        model.uid, 
        NotificationType.MODEL_UPDATE, 
        {
            'change_id': change.id,
            'model_name': model_name,
        }
    )
    return model

def toggle_like_model(model_id, user):
    repo = ModelsDBRepo()
    model = retrieve_model(model_id)
    user = retrieve_user(user.uid)
    if model.id in user.liked_models:
        repo.unlike_model(model_id, user.uid)
    else:
        repo.like_model(model_id, user.uid)
    return "done"


