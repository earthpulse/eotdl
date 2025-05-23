from datetime import datetime

from ..changes import retrieve_change
from ...models import ChangeStatus, ChangeType, Dataset, Model, NotificationType, Pipeline
from ...repos import ChangesDBRepo

def accept_change(change_id, user):
   # avoid circular imports
   from ..datasets import update_dataset
   from ..models import update_model
   from ..notifications import create_notification
   from ..pipelines import update_pipeline

   change = retrieve_change(change_id)
   changes_repo = ChangesDBRepo()
   if change.status != ChangeStatus.PENDING:
      raise Exception("Change is not pending")
   if change.type == ChangeType.DATASET_UPDATE:
      updated_dataset = Dataset(**change.payload)
      update_dataset(change.payload['id'], user, updated_dataset)
      change.status = ChangeStatus.APPROVED
      change.updatedAt = datetime.now()
      changes_repo.update_change(change.id, change.model_dump())
      create_notification(
         change.uid, 
         NotificationType.DATASET_UPDATE_REQUEST_ACCEPTED, 
         {
               'change_id': change.id,
               "message": f"Your dataset update request for {change.payload['name']} has been accepted."
         }
      )
   elif change.type == ChangeType.MODEL_UPDATE:
      updated_model = Model(**change.payload)
      update_model(change.payload['id'], user, updated_model)
      change.status = ChangeStatus.APPROVED
      change.updatedAt = datetime.now()
      changes_repo.update_change(change.id, change.model_dump())
      create_notification(
         change.uid, 
         NotificationType.MODEL_UPDATE_REQUEST_ACCEPTED, 
         {
               'change_id': change.id,
               "message": f"Your model update request for {change.payload['name']} has been accepted."
         }
      )
   elif change.type == ChangeType.PIPELINE_UPDATE:
      updated_pipeline = Pipeline(**change.payload)
      update_pipeline(change.payload['id'], user, updated_pipeline)
      change.status = ChangeStatus.APPROVED
      change.updatedAt = datetime.now()
      changes_repo.update_change(change.id, change.model_dump())
      create_notification(
         change.uid, 
         NotificationType.PIPELINE_UPDATE_REQUEST_ACCEPTED, 
         {
               'change_id': change.id,
               "message": f"Your pipeline update request for {change.payload['name']} has been accepted."
         }
      )
   return change