from pydantic import BaseModel
import typing 

from ...errors import DatasetDoesNotExistError, TierLimitError
from ...models import Usage, User, Limits

class DownloadDataset():
    def __init__(self, db_repo, os_repo):
        self.db_repo = db_repo
        self.os_repo = os_repo

    class Inputs(BaseModel):
        id: str
        uid: str

    class Outputs(BaseModel):
        data_stream: typing.Any
        object_info: typing.Any
        name: str

    def __call__(self, inputs: Inputs) -> Outputs:
        # check if user can download dataset
        data = self.db_repo.retrieve('users', inputs.uid, 'uid')
        user = User(**data)
        data = self.db_repo.find_one_by_name('tiers', user.tier)
        limits = Limits(**data['limits'])
        usage = self.db_repo.find_in_time_range('usage',  inputs.uid, 'dataset_download', 'type')
        if len(usage) + 1 >= limits.datasets.download:
            raise TierLimitError("You cannot download more than {} datasets per day".format(limits.datasets.download))
        # check if dataset exists
        data = self.db_repo.retrieve('datasets', inputs.id)
        if not data:
            raise DatasetDoesNotExistError()
        # report usage
        usage = Usage.DatasetDownload(uid=inputs.uid, payload={'dataset': inputs.id})
        self.db_repo.persist('usage', usage.dict())
        # download
        return self.Outputs(
            data_stream=self.os_repo.data_stream,
            object_info=self.os_repo.object_info(inputs.id),
            name=data['name'],
        )