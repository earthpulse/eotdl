from pydantic import BaseModel, Field, field_validator
from enum import Enum
from datetime import datetime

class NotificationType(str, Enum):
    DATASET_UPDATE = "dataset_update"
    MODEL_UPDATE = "model_update"
    DATASET_UPDATE_REQUEST_DECLINED = "dataset_update_request_declined"
    DATASET_UPDATE_REQUEST_ACCEPTED = "dataset_update_request_accepted"
    MODEL_UPDATE_REQUEST_DECLINED = "model_update_request_declined"
    MODEL_UPDATE_REQUEST_ACCEPTED = "model_update_request_accepted"

class NotificationStatus(str, Enum):
    UNREAD = "unread"
    READ = "read"
    ACCEPTED = "accepted"
    DECLINED = "declined"

class Notification(BaseModel):
    uid: str
    id: str
    type: NotificationType
    status: NotificationStatus = NotificationStatus.UNREAD
    payload: dict = Field(default_factory=dict)
    createdAt: datetime = Field(default_factory=datetime.now)
    updatedAt: datetime = Field(default_factory=datetime.now)

    @field_validator("payload")
    def check_payload_is_valid(cls, payload, values):
        if values.data.get('type') == NotificationType.DATASET_UPDATE or values.data.get('type') == NotificationType.MODEL_UPDATE:
            if 'change_id' not in payload:
                raise ValueError("Payload must contain change_id for dataset updates")
        return payload