from ...repos import ModelsDBRepo


def deactivate_model(model_name: str):
    repo = ModelsDBRepo()
    model = repo.find_one_by_name(model_name)
    if model.get("active") is False:
        raise Exception(f"Model {model_name} is already deactivated.")
    repo.deactivate_model(model_name)
    return f"Model {model_name} has been deactivated."