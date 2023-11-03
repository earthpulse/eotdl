from pydantic import BaseModel
from datetime import datetime

class BaseUsage(BaseModel):
    uid: str
    type: str
    timestamp: datetime = datetime.now()
    payload: dict

class Usage:
    class DatasetIngested(BaseUsage):
        type: str = 'dataset_ingested'
    class DatasetDownload(BaseUsage):
        type = 'dataset_download'

class DatasetLimits(BaseModel):
    upload: int
    download: int
<<<<<<< HEAD:apis/eotdl/src/models/usage.py

class Limits(BaseModel):
    datasets: DatasetLimits
=======
    count: int


class ModelLimits(BaseModel):
    upload: int
    download: int
    count: int


class Limits(BaseModel):
    datasets: DatasetLimits
    models: ModelLimits
>>>>>>> develop:api/api/src/models/usage.py
