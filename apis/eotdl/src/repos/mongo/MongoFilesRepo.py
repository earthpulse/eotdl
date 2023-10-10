from .MongoRepo import MongoRepo


class MongoFilesRepo(MongoRepo):
    def __init__(self):
        super().__init__()

    def retrieve_file(self, files_id, filename, version):
        return self.retrieve2(
            "files",
            {
                "id": files_id,
                "files": {"$elemMatch": {"name": filename, "version": version}},
            },
            {"files.$": 1},
        )

    def add_file(self, files_id, file):
        return self.push("files", files_id, {"files": file})

    def update_file(self, files_id, filename, version, file):
        return self._update(
            "files",
            {
                "id": files_id,
                "files": {
                    "$elemMatch": {
                        "name": filename,
                        "version": version,
                    }
                },
            },
            {"$set": {"files.$": file}},
        )

    def add_folder_version(self, files_id, folder_name, version):
        return self._update(
            "files",
            {"id": files_id, "folders.name": folder_name},
            {"$addToSet": {"folders.$.versions": version}},
        )

    def add_folder(self, files_id, folder):
        return self.push("files", files_id, {"folders": folder})
