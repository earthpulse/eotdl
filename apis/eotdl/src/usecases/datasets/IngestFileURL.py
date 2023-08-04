from pydantic import BaseModel
import os

from .IngestFile import IngestFile


class IngestFileURL(IngestFile):
    def __init__(self, db_repo, os_repo):
        super().__init__(db_repo, os_repo)

    class Inputs(BaseModel):
        dataset: str
        file: str
        uid: str
        checksum: str = None

    def get_file_name(self, file):
        return file.split("/")[-1]

    def persist_file(self, file, dataset_id, filename):
        return self.os_repo.persist_file_url(file, dataset_id, filename)
