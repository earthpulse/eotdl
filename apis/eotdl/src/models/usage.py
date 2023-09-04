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

class Limits(BaseModel):
    datasets: DatasetLimits