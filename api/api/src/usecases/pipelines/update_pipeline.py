from datetime import datetime

from ...repos import PipelinesDBRepo
from .retrieve_pipeline import retrieve_pipeline, retrieve_pipeline_by_name
from ...errors import PipelineAlreadyExistsError, PipelineDoesNotExistError
from ...models import Pipeline, ChangeType, NotificationType
from ..notifications import create_notification
from ..changes import create_change
from ..user import retrieve_user

def update_pipeline(
    pipeline_id, user, pipeline
):
    _pipeline = retrieve_pipeline(pipeline_id)
    if user.uid != _pipeline.uid:
        # user is not the owner of the pipeline, so any change should be approved by the owner or moderators
        return propose_pipeline_update(_pipeline.name, user, pipeline)
    
    # update name
    if pipeline.name != _pipeline.name:
        try:
            __pipeline = retrieve_pipeline_by_name(pipeline.name)
            if __pipeline.id != pipeline_id:
                raise PipelineAlreadyExistsError()
        except PipelineDoesNotExistError:
            pass

    # # validate tags
    # if tags:
    #     tags_data = repo.retrieve_tags()
    #     all_tags = [tag["name"] for tag in tags_data]
    #     for tag in tags:
    #         if tag not in all_tags:
    #             raise InvalidTagError()

    # update dataset
    _pipeline.name = pipeline.name
    _pipeline.metadata = pipeline.metadata
    _pipeline.updatedAt = datetime.now()
    # update pipeline in db
    repo = PipelinesDBRepo()
    repo.update_pipeline(pipeline_id, _pipeline.model_dump())
    return _pipeline

def propose_pipeline_update(pipeline_name, user, pipeline):
    change = create_change(
        user,
        ChangeType.PIPELINE_UPDATE,
        pipeline,
    )
    create_notification(
        pipeline.uid, 
        NotificationType.PIPELINE_UPDATE, 
        {
            'change_id': change.id,
            'pipeline_name': pipeline_name,
        }
    )
    return pipeline

def toggle_like_pipeline(pipeline_id, user):
    repo = PipelinesDBRepo()
    pipeline = retrieve_pipeline(pipeline_id)
    user = retrieve_user(user.uid)
    if pipeline.id in user.liked_pipelines:
        repo.unlike_pipeline(pipeline_id, user.uid)
    else:
        repo.like_pipeline(pipeline_id, user.uid)
    return "done"


