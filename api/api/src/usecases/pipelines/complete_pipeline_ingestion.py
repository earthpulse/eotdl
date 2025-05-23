from ...repos import PipelinesDBRepo
from ...models import Version
from .retrieve_pipeline import retrieve_owned_pipeline

def complete_pipeline_ingestion(pipeline_id, user, version, size):
    pipeline_repo = PipelinesDBRepo()
    pipeline = retrieve_owned_pipeline(pipeline_id, user.uid)
    if version == 1:
        pipeline.versions[0].size = size
        return pipeline_repo.update_pipeline(pipeline.id, pipeline.model_dump())
    latest_version = Version(version_id=version, size=size)
    version_ids = sorted([v.version_id for v in pipeline.versions])
    assert latest_version.version_id not in version_ids, "Latest version already exists"
    assert len(version_ids) == latest_version.version_id - 1, "Latest version is not the next version"
    return pipeline_repo.create_pipeline_version(pipeline, latest_version.model_dump())