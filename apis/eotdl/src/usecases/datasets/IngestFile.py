from pydantic import BaseModel
import typing
from typing import Union
from datetime import datetime

from ...models import Dataset, Usage, User, Limits, File, STACDataset
from ...errors import (
    TierLimitError,
    DatasetDoesNotExistError,
    ChecksumMismatch,
)


class IngestFile:
    def __init__(self, db_repo, os_repo):
        self.db_repo = db_repo
        self.os_repo = os_repo

    class Inputs(BaseModel):
        dataset_id: str
        file: typing.Any
        uid: str
        version: int
        parent: str
        checksum: Union[str, None] = None

    class Outputs(BaseModel):
        dataset_id: str
        dataset_name: str
        file_name: str

    def get_file_name(self, file):
        return file.filename

    def persist_file(self, file, dataset_id, filename):
        return self.os_repo.persist_file(file.file, dataset_id, filename)

    async def __call__(self, inputs: Inputs) -> Outputs:
        # check if dataset exists
        data = self.db_repo.retrieve("datasets", inputs.dataset_id)
        versions = [v['version_id'] for v in data['versions']]
        if not data or not inputs.version in versions:
            raise DatasetDoesNotExistError()
        dataset = Dataset(**data) if data["quality"] == 0 else STACDataset(**data)
        # check if user can ingest file
        data = self.db_repo.retrieve("users", inputs.uid, "uid")
        user = User(**data)
        data = self.db_repo.find_one_by_name("tiers", user.tier)
        # check user owns dataset
        if dataset.uid != inputs.uid:
            raise DatasetDoesNotExistError()
        # check if user can ingest file
        filename = self.get_file_name(inputs.file)
        if inputs.parent != ".":
            filename = inputs.parent + "/" + filename
        print(filename)
        # save file in storage
        filename, filename0 = self.persist_file(inputs.file, dataset.id, filename)
        print("filename", filename, filename0)
        # calculate checksum
        checksum = await self.os_repo.calculate_checksum(dataset.id, filename)
        if inputs.checksum and checksum != inputs.checksum:
            self.os_repo.delete_file(dataset.id, inputs.file.name)
            if len(dataset.files) == 0:
                self.db_repo.delete("datasets", dataset.id)
            raise ChecksumMismatch()
        file_size = self.os_repo.object_info(dataset.id, filename).size
        if dataset.quality == 0:
            # TODO: handle existing files
            file = [f for f in dataset.files if f.name == filename0]
            print(dataset.files, file)
            if len(file) == 1:
                # update file
                file = file[0]
                print(filename0, "already exists")
                if file.checksum != checksum: # the file has been modified
                    print("new version of", filename0, filename)
                    dataset.files.append(File(name=filename, size=file_size, checksum=checksum, versions=[inputs.version]))
                else:
                    print("same version of", filename0, filename)
                    self.os_repo.delete(dataset.id, filename)
                    file = File(name=filename0, size=file_size, checksum=checksum, versions=file.versions + [inputs.version])
                    dataset.files = [f for f in dataset.files if f.name != filename0] + [file]
            elif len(file) == 0:
                print("new file", filename)
                dataset.files.append(File(name=filename, size=file_size, checksum=checksum, versions=[inputs.version]))
            else: # dataset exists and is the same
                pass
        version = [v for v in dataset.versions if v.version_id == inputs.version][0]
        version.size += file_size  # for Q0+ will add, so put to 0 before if necessary
        dataset.updatedAt = datetime.now()
        self.db_repo.update("datasets", dataset.id, dataset.dict())
        # report usage
        usage = Usage.FileIngested(
            uid=inputs.uid,
            payload={
                "dataset": dataset.id,
                "file": filename,
                "size": file_size,
            },
        )
        self.db_repo.persist("usage", usage.dict())
        return self.Outputs(
            dataset_id=dataset.id,
            dataset_name=dataset.name,
            file_name=filename,
        )
