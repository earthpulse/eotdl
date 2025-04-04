from ...repos import ModelsDBRepo


def deactivate_model(model_id: str):
    repo = ModelsDBRepo()
    model = repo.find_one_by_field('id', model_id)
    if model.get("active") is False:
        raise Exception(f"Model {model_id} is already deactivated.")
    repo.deactivate_model(model_id)
    return f"Model {model_id} has been deactivated."