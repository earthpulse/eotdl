from pydantic import BaseModel, Field
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
    id: str
    uid: str
    name: str
    email: str
    picture: str
    createdAt: datetime = Field(default_factory=datetime.now)
    updatedAt: datetime = Field(default_factory=datetime.now)
    dataset_count: int = 0
    models_count: int = 0
    pipelines_count: int = 0
    tier: Tier = Tier.FREE
    liked_datasets: list = []
    liked_models: list = []
    terms: TermsAndConditions = TermsAndConditions()
    verified: bool = False
    pseudocredits: int = 0
    credits: int = 0

    # class Config:
    #     use_enum_values = True


class ApiKey(BaseModel):
    id: str
    uid: str
    createdAt: datetime = Field(default_factory=datetime.now)
