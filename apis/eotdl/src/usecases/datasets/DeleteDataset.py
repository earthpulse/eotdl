from pydantic import BaseModel

from ...errors import DatasetDoesNotExistError
from ...models import Dataset


class DeleteDataset:
    def __init__(self, db_repo, os_repo):
        self.db_repo = db_repo
        self.os_repo = os_repo

    class Inputs(BaseModel):
        name: str

    class Outputs(BaseModel):
        message: str

    def __call__(self, inputs: Inputs) -> Outputs:
        # check if dataset exists
        data = self.db_repo.find_one_by_name("datasets", inputs.name)
        if data is None:
            raise DatasetDoesNotExistError()
        dataset = Dataset(**data)
        # remove from os
        for file in dataset.files:
            self.os_repo.delete(dataset.id, file.name)
        # remove from db
        self.db_repo.delete("datasets", dataset.id)
        # update user dataset count
        self.db_repo.increase_counter("users", "uid", dataset.uid, "dataset_count", -1)
        return self.Outputs(message="Dataset deleted successfully")
