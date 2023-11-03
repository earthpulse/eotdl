from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class Tier(Enum):
    FREE = 'free'
    DEV = 'dev'


class User(BaseModel):
    id: str
    uid: str
    name: str
    email: str
    picture: str
    createdAt: datetime = datetime.now()
    updatedAt: datetime = datetime.now()
    dataset_count: int = 0
    model_count: int = 0
    tier: Tier = Tier.FREE
    liked_datasets: list = []
<<<<<<< HEAD:apis/eotdl/src/models/user.py
=======
    liked_models: list = []
    terms: TermsAndConditions = TermsAndConditions()
>>>>>>> develop:api/api/src/models/user.py

    class Config:
       use_enum_values = True

