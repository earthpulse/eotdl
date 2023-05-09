from ...repos import DBRepo, OSRepo, S3Repo
from .IngestDataset import IngestDataset
from .RetrieveDatasets import RetrieveDatasets
from .RetrieveOneDatasetByName import RetrieveOneDatasetByName
from .DownloadDataset import DownloadDataset
from .EditDataset import EditDataset
from .RetrieveDatasetsLeaderboard import RetrieveDatasetsLeaderboard
from ..tags import retrieve_tags
from .LikeDataset import LikeDataset
from .RetrieveLikedDatasets import RetrieveLikedDatasets
from .RetrievePopularDatasets import RetrievePopularDatasets
from .IngestDatasetChunk import IngestDatasetChunk
from .DeleteDataset import DeleteDataset
from .GenerateUploadId import GenerateUploadId
from .CompleteMultipartUpload import CompleteMultipartUpload


def ingest_dataset(file, name, description, user):
    db_repo = DBRepo()
    os_repo = OSRepo()
    ingest = IngestDataset(db_repo, os_repo)
    inputs = ingest.Inputs(
        name=name, file=file.file, size=file.size, uid=user.uid, description=description
    )
    outputs = ingest(inputs)
    return outputs.dataset


def retrieve_datasets(limit):
    db_repo = DBRepo()
    retrieve = RetrieveDatasets(db_repo)
    inputs = retrieve.Inputs(limit=limit)
    outputs = retrieve(inputs)
    return outputs.datasets


def retrieve_dataset_by_name(name):
    db_repo = DBRepo()
    retrieve = RetrieveOneDatasetByName(db_repo)
    inputs = retrieve.Inputs(name=name)
    outputs = retrieve(inputs)
    return outputs.dataset


def retrieve_liked_datasets(user):
    db_repo = DBRepo()
    retrieve = RetrieveLikedDatasets(db_repo)
    inputs = retrieve.Inputs(uid=user.uid)
    outputs = retrieve(inputs)
    return outputs.datasets


def retrieve_popular_datasets(limit):
    db_repo = DBRepo()
    retrieve = RetrievePopularDatasets(db_repo)
    inputs = retrieve.Inputs(limit=limit)
    outputs = retrieve(inputs)
    return outputs.datasets


def download_dataset(id, user):
    db_repo = DBRepo()
    os_repo = OSRepo()
    retrieve = DownloadDataset(db_repo, os_repo)
    inputs = retrieve.Inputs(id=id, uid=user.uid)
    outputs = retrieve(inputs)
    return outputs.data_stream, outputs.object_info, outputs.name


def edit_dataset(id, name, description, tags, user):
    db_repo = DBRepo()
    edit = EditDataset(db_repo, retrieve_tags)
    inputs = edit.Inputs(
        id=id, name=name, description=description, tags=tags, uid=user.uid
    )
    outputs = edit(inputs)
    return outputs.dataset


def retrieve_datasets_leaderboard():
    db_repo = DBRepo()
    retrieve = RetrieveDatasetsLeaderboard(db_repo)
    inputs = retrieve.Inputs()
    outputs = retrieve(inputs)
    return outputs.leaderboard


def like_dataset(id, user):
    db_repo = DBRepo()
    like = LikeDataset(db_repo)
    inputs = like.Inputs(id=id, uid=user.uid)
    outputs = like(inputs)
    return outputs.message


def delete_dataset(name):
    db_repo = DBRepo()
    os_repo = OSRepo()
    delete = DeleteDataset(db_repo, os_repo)
    inputs = DeleteDataset.Inputs(name=name)
    outputs = delete(inputs)
    return outputs.message


def generate_upload_id(name, description, user):
    db_repo = DBRepo()
    os_repo = OSRepo()
    s3_repo = S3Repo()
    generate = GenerateUploadId(db_repo, os_repo, s3_repo)
    inputs = generate.Inputs(
        uid=user.uid,
        name=name,
        description=description,
    )
    outputs = generate(inputs)
    return outputs.dataset_id, outputs.upload_id


def ingest_dataset_chunk(
    chunk,
    part_number,
    id,
    upload_id,
):
    os_repo = OSRepo()
    s3_repo = S3Repo()
    ingest = IngestDatasetChunk(os_repo, s3_repo)
    inputs = ingest.Inputs(
        chunk=chunk, id=id, upload_id=upload_id, part_number=part_number
    )
    outputs = ingest(inputs)
    return outputs.id, outputs.upload_id


def complete_multipart_upload(user, name, description, dataset_id, upload_id):
    db_repo = DBRepo()
    os_repo = OSRepo()
    s3_repo = S3Repo()
    complete = CompleteMultipartUpload(db_repo, os_repo, s3_repo)
    inputs = complete.Inputs(
        uid=user.uid,
        name=name,
        description=description,
        id=dataset_id,
        upload_id=upload_id,
    )
    outputs = complete(inputs)
    return outputs.dataset
