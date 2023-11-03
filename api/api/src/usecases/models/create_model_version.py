from .retrieve_model import retrieve_owned_model
from ...models import Version
from ...repos import ModelsDBRepo


def create_model_version(user, model_id):
    repo = ModelsDBRepo()
    model = retrieve_owned_model(model_id, user.uid)
    current_versions = sorted(model.versions, key=lambda x: x.version_id)
    last_version = current_versions[-1].version_id if len(current_versions) > 0 else 0
    version = Version(version_id=last_version + 1)
    repo.create_model_version(model, version.model_dump())
    return version.version_id
