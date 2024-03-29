from ..repos import DatasetsAPIRepo


def update_dataset(dataset_id, metadata, content, user):
    repo = DatasetsAPIRepo()
    data, error = repo.update_dataset(
        dataset_id,
        metadata.authors,
        metadata.source,
        metadata.license,
        metadata.thumbnail,
        content,
        user,
    )
    if error:
        raise Exception(error)
    return data
