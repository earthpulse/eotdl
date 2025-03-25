from ...repos import OSRepo, ModelsDBRepo
from ...models import Version
from .retrieve_model import retrieve_model, retrieve_owned_model

def complete_model_ingestion(model_id, user, version, size):
    model_repo = ModelsDBRepo()
    model = retrieve_owned_model(model_id, user.uid)
    if version == 1:
        model.versions[0].size = size
        return model_repo.update_model(model.id, model.model_dump())
    latest_version = Version(version_id=version, size=size)
    version_ids = sorted([v.version_id for v in model.versions])
    assert latest_version.version_id not in version_ids, "Latest version already exists"
    assert len(version_ids) == latest_version.version_id - 1, "Latest version is not the next version"
    return model_repo.create_model_version(model, latest_version.model_dump())