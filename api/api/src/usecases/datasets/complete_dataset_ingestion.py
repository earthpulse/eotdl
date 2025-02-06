from ...repos import OSRepo, DatasetsDBRepo
from ...models import Version
from .retrieve_dataset import retrieve_dataset, retrieve_owned_dataset

def complete_dataset_ingestion(dataset_id, user, version, size):
    dataset_repo = DatasetsDBRepo()
    dataset = retrieve_owned_dataset(dataset_id, user.uid)
    if version == 1:
        dataset.versions[0].size = size
        return dataset_repo.update_dataset(dataset.id, dataset.model_dump())
    latest_version = Version(version_id=version, size=size)
    version_ids = sorted([v.version_id for v in dataset.versions])
    assert latest_version.version_id not in version_ids, "Latest version already exists"
    assert len(version_ids) == latest_version.version_id - 1, "Latest version is not the next version"
    return dataset_repo.create_dataset_version(dataset, latest_version.model_dump())