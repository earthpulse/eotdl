from ...models.user import User
from .retrieve_model import retrieve_owned_model
from ...repos import ModelsDBRepo


def make_model_private(model_id: str, user: User):
    """
    Make a model private.
    """
    model = retrieve_owned_model(model_id, user.uid)
    repo = ModelsDBRepo()
    if user.uid in model.allowed_users:
        raise Exception("This model is already private")
    repo.allow_user_to_model(model_id, user.uid)
    return f"Model {model.name} has been made private."


def allow_user_to_private_model(
    model_id: str,
    user: User,
    user_id: str,
):
    """
    Allow a user to access a private model.
    """
    model = retrieve_owned_model(model_id, user.uid)
    repo = ModelsDBRepo()
    if not user.uid in model.allowed_users:
        raise Exception("This is not a private model")
    repo.allow_user_to_model(model_id, user_id)
    return f"User {user_id} has been allowed to access the private model {model.name}."
