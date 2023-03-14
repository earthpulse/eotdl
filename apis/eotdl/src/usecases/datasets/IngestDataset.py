from pydantic import BaseModel
import typing

from ...models import Dataset
from ...errors import DatasetAlreadyExistsError

class IngestDataset():
    def __init__(self, db_repo, os_repo):
        self.db_repo = db_repo
        self.os_repo = os_repo

    class Inputs(BaseModel):
        name: str
        description: str
        file: typing.Any
        uid: str

    class Outputs(BaseModel):
        dataset: Dataset

    def __call__(self, inputs: Inputs) -> Outputs:
        # check if name already exists
        if self.db_repo.find_one_by_name('datasets', inputs.name):
            raise DatasetAlreadyExistsError()
        # generate new id 
        id = self.db_repo.generate_id()
        # save file in storage
        self.os_repo.persist_file(inputs.file, id)
        # save dataset in db
        dataset = Dataset(uid=inputs.uid, id=id, name=inputs.name, description=inputs.description)
        self.db_repo.persist('datasets', dataset.dict(), id)
        return self.Outputs(dataset=dataset)