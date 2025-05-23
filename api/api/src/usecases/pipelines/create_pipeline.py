from ...models import Pipeline, Metadata
from ...errors import (
    PipelineAlreadyExistsError,
    PipelineDoesNotExistError,
)
from ...repos import PipelinesDBRepo

from .retrieve_pipeline import retrieve_pipeline_by_name
from ..user import check_user_can_create_pipeline


def create_pipeline(user, name, authors, source, license, thumbnail, description):
    repo = PipelinesDBRepo()
    try:
        retrieve_pipeline_by_name(name)
        raise PipelineAlreadyExistsError()
    except PipelineDoesNotExistError:
        check_user_can_create_pipeline(user)
        id = repo.generate_id()
        pipeline = Pipeline(
            uid=user.uid,
            id=id,
            name=name,
            metadata=Metadata(
                authors=authors,
                source=source,
                license=license,
                thumbnail=thumbnail,
                description=description,
            ),
        )
        repo.persist_pipeline(pipeline.model_dump(), pipeline.id)
        repo.increase_user_pipeline_count(user.uid)
        return pipeline
