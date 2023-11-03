from ...repos import ModelsDBRepo
from .retrieve_model import retrieve_model
from ..user import retrieve_user


def toggle_like_model(model_id, user):
    repo = ModelsDBRepo()
    model = retrieve_model(model_id)
    user = retrieve_user(user.uid)
    if model.id in user.liked_models:
        repo.unlike_model(model_id, user.uid)
    else:
        repo.like_model(model_id, user.uid)
    return "done"
