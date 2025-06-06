from pydantic import BaseModel
from datetime import datetime


class BaseUsage(BaseModel):
    uid: str
    type: str
    timestamp: datetime = datetime.now()
    payload: dict


class Usage:
    class FileIngested(BaseUsage):
        type: str = "file_ingested"

    class FileDownload(BaseUsage):
        type: str = "file_download"


class DatasetLimits(BaseModel):
    upload: int
    download: int
    count: int


class ModelLimits(BaseModel):
    upload: int
    download: int
    count: int

class PipelineLimits(BaseModel):
    upload: int
    download: int
    count: int

class Limits(BaseModel):
    datasets: DatasetLimits
    models: ModelLimits
    pipelines: PipelineLimits
