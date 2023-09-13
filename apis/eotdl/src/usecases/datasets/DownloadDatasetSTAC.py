from pydantic import BaseModel
import json

from ...errors import DatasetDoesNotExistError
from ...models import STACDataset, User


class DownloadDatasetSTAC:
    def __init__(self, db_repo, geodb_repo, retrieve_user_credentials):
        self.db_repo = db_repo
        self.geodb_repo = geodb_repo
        self.retrieve_user_credentials = retrieve_user_credentials

    class Inputs(BaseModel):
        dataset_id: str
        user: User

    class Outputs(BaseModel):
        stac: dict

    def __call__(self, inputs: Inputs) -> Outputs:
        # check if dataset exists and user is owner
        data = self.db_repo.retrieve("datasets", inputs.dataset_id)
        if not data:
            raise DatasetDoesNotExistError()
        dataset = STACDataset(**data)
        if dataset.uid != inputs.user.uid:
            raise DatasetDoesNotExistError()
        # retrieve from geodb
        credentials = self.retrieve_user_credentials(inputs.user)
        self.geodb_repo = self.geodb_repo(credentials)
        gdf = self.geodb_repo.retrieve(inputs.dataset_id)
        # report usage
        self.db_repo.increase_counter("datasets", "id", dataset.id, "downloads")
        return self.Outputs(stac=json.loads(gdf.to_json()))
