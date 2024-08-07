from ...repos import FilesDBRepo


def retrieve_files(versions, files_id, version=None):
    files_repo = FilesDBRepo()
    versions = sorted(versions, key=lambda x: x.version_id)
    if len(versions) == 0:
        raise Exception("No versions found")
    if version is None:
        # version = versions[-1].version_id
        print("No version provided, retrieving all files")
    if version and version not in [v.version_id for v in versions]:
        raise Exception("Version not found")
    data = files_repo.retrieve_files(files_id, version)
    if len(data) != 1:
        raise Exception("No files found")
    files = (
        [
            {
                "filename": f["name"],
                "version": f["version"],
                "checksum": f["checksum"],
                "size": f["size"],
            }
            for f in data[0]["files"]
        ]
        if len(data[0]["files"]) > 0
        else []
    )
    return files
