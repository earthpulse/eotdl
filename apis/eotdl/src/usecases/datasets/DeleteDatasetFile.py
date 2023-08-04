from pydantic import BaseModel
from datetime import datetime

from ...errors import (
    DatasetDoesNotExistError,
    UserUnauthorizedError,
    FileDoesNotExistError,
)
from ...models import Dataset


class DeleteDatasetFile:
    def __init__(self, db_repo, os_repo):
        self.db_repo = db_repo
        self.os_repo = os_repo

    class Inputs(BaseModel):
        uid: str
        dataset_id: str
        file_name: str

    class Outputs(BaseModel):
        message: str

    def __call__(self, inputs: Inputs) -> Outputs:
        # check if dataset exists
        data = self.db_repo.retrieve("datasets", inputs.dataset_id)
        if data is None:
            raise DatasetDoesNotExistError()
        dataset = Dataset(**data)
        # check that user is owner
        if inputs.uid != dataset.uid:
            raise UserUnauthorizedError()
        # check if file exists
        if inputs.file_name not in [file.name for file in dataset.files]:
            raise FileDoesNotExistError()
        file = [file for file in dataset.files if file.name == inputs.file_name][0]
        # remove from os
        self.os_repo.delete(dataset.id, inputs.file_name)
        # update db
        dataset.files = [
            file for file in dataset.files if file.name != inputs.file_name
        ]
        dataset.updatedAt = datetime.now()
        dataset.size = dataset.size - file.size
        self.db_repo.update("datasets", dataset.id, dataset.dict())
        return self.Outputs(message="File deleted successfully")
