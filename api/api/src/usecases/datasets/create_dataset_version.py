from .retrieve_dataset import retrieve_owned_dataset
from ...models import Version
from ...repos import DatasetsDBRepo


def create_dataset_version(user, dataset_id):
    repo = DatasetsDBRepo()
    dataset = retrieve_owned_dataset(dataset_id, user)
    current_versions = sorted(dataset.versions, key=lambda x: x.version_id)
    last_version = current_versions[-1].version_id if len(current_versions) > 0 else 0
    version = Version(version_id=last_version + 1)
    repo.create_dataset_version(dataset, version.model_dump())
    return version.version_id
