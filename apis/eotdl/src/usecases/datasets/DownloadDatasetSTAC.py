from pydantic import BaseModel
import json

from ...errors import DatasetDoesNotExistError, TierLimitError, FileDoesNotExistError
from ...models import Usage, User, Limits, Dataset


class DownloadDatasetSTAC:
    def __init__(self, db_repo, geodb_repo):
        self.db_repo = db_repo
        self.geodb_repo = geodb_repo

    class Inputs(BaseModel):
        dataset_id: str
        uid: str

    class Outputs(BaseModel):
        stac: dict

    def __call__(self, inputs: Inputs) -> Outputs:
        # check if dataset exists
        data = self.db_repo.retrieve("datasets", inputs.dataset_id)
        if not data:
            raise DatasetDoesNotExistError()
        dataset = Dataset(**data)
        gdf = self.geodb_repo.retrieve(dataset.name)
        return self.Outputs(stac=json.loads(gdf.to_json()))
