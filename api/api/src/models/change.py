from pydantic import BaseModel, Field, field_validator
from enum import Enum
from datetime import datetime

from .dataset import Dataset
from .model import Model

class ChangeType(str, Enum):
    DATASET_UPDATE = "dataset_update"
    MODEL_UPDATE = "model_update"
    PIPELINE_UPDATE = "pipeline_update"

class ChangeStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Change(BaseModel):
    uid: str
    id: str
    type: ChangeType
    payload: dict | Dataset | Model
    status: ChangeStatus = ChangeStatus.PENDING
    createdAt: datetime = Field(default_factory=datetime.now)
    updatedAt: datetime = Field(default_factory=datetime.now)

