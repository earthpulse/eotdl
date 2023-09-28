from pydantic import BaseModel
from datetime import datetime

from ...errors import (
    DatasetDoesNotExistError,
    UserUnauthorizedError,
    FileDoesNotExistError,
)
from ...models import Dataset, Version


class CreateDatasetVersion:
    def __init__(self, db_repo):
        self.db_repo = db_repo

    class Inputs(BaseModel):
        uid: str
        dataset_id: str

    class Outputs(BaseModel):
        version: int

    def __call__(self, inputs: Inputs) -> Outputs:
        # check if dataset exists
        data = self.db_repo.retrieve("datasets", inputs.dataset_id)
        if data is None:
            raise DatasetDoesNotExistError()
        # check that user is owner
        if inputs.uid != data['uid']:
            raise UserUnauthorizedError()
        # get last version
        last_version = data['versions'][-1]['version_id'] if len(data['versions']) > 0 else 0
        # create new version
        version = Version(version_id=last_version + 1)
        self.db_repo.update(
            "datasets",
            inputs.dataset_id,
            {"versions": data['versions'] + [version.dict()], "updated_at": datetime.now()},
        )
        return self.Outputs(version=version.version_id)
