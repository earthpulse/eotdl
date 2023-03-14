from pydantic import BaseModel
import typing 

from ...errors import DatasetDoesNotExistError

class DownloadDataset():
    def __init__(self, db_repo, os_repo):
        self.db_repo = db_repo
        self.os_repo = os_repo

    class Inputs(BaseModel):
        id: str

    class Outputs(BaseModel):
        data_stream: typing.Any
        object_info: typing.Any
        name: str

    def __call__(self, inputs: Inputs) -> Outputs:
        data = self.db_repo.retrieve('datasets', inputs.id)
        if not data:
            raise DatasetDoesNotExistError()
        # url = self.os_repo.retrieve_object_url(inputs.id)
        return self.Outputs(
            data_stream=self.os_repo.data_stream,
            object_info=self.os_repo.object_info(inputs.id),
            name=data['name'],
        )