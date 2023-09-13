from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class Tier(str, Enum):
    FREE = "free"
    DEV = "dev"


class TermsAndConditions(BaseModel):
    geodb: bool = False
    sentinelhub: bool = False
    eoxhub: bool = False
    eotdl: bool = False


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
    terms: TermsAndConditions = TermsAndConditions()

    # class Config:
    #     use_enum_values = True
