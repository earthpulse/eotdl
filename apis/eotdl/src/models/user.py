from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class Tier(str, Enum):
    FREE = "free"
    DEV = "dev"


class User(BaseModel):
    uid: str
    name: str
    email: str
    picture: str
    createdAt: datetime = datetime.now()
    updatedAt: datetime = datetime.now()
    dataset_count: int = 0
    models_count: int = 0
    tier: Tier = Tier.FREE
    liked_datasets: list = []

    # class Config:
    #     use_enum_values = True
