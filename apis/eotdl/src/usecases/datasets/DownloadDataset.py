from pydantic import BaseModel
import typing

from ...errors import DatasetDoesNotExistError, TierLimitError, FileDoesNotExistError
from ...models import Usage, User, Limits, Dataset


class DownloadDataset:
    def __init__(self, db_repo, os_repo):
        self.db_repo = db_repo
        self.os_repo = os_repo

    class Inputs(BaseModel):
        id: str
        uid: str
        file: str

    class Outputs(BaseModel):
        data_stream: typing.Any
        object_info: typing.Any
        name: str

    def __call__(self, inputs: Inputs) -> Outputs:
        # check if user can download dataset
        data = self.db_repo.retrieve("users", inputs.uid, "uid")
        user = User(**data)
        data = self.db_repo.find_one_by_name("tiers", user.tier)
        limits = Limits(**data["limits"])
        usage = self.db_repo.find_in_time_range(
            "usage", inputs.uid, "dataset_download", "type"
        )
        if len(usage) + 1 >= limits.datasets.download:
            raise TierLimitError(
                "You cannot download more than {} files per day".format(
                    limits.datasets.download
                )
            )
        # check if dataset exists
        data = self.db_repo.retrieve("datasets", inputs.id)
        if not data:
            raise DatasetDoesNotExistError()
        # check if file exists
        dataset = Dataset(**data)
        if inputs.file not in [f.name for f in dataset.files]:
            raise FileDoesNotExistError()
        # report usage
        object_info = self.os_repo.object_info(inputs.id, inputs.file)
        usage = Usage.FileDownload(
            uid=inputs.uid,
            payload={
                "dataset": inputs.id,
                "file": inputs.file,
                "size": object_info.size,
            },
        )
        self.db_repo.persist("usage", usage.dict())
        self.db_repo.increase_counter("datasets", "id", inputs.id, "downloads")
        # download
        return self.Outputs(
            data_stream=self.os_repo.data_stream,
            object_info=object_info,
            name=inputs.file,
        )
