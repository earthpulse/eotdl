from ...repos import DBRepo, OSRepo, S3Repo
from .IngestFile import IngestFile
from .UpdateDataset import UpdateDataset
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


async def ingest_file(file, dataset, checksum, user):
    db_repo = DBRepo()
    os_repo = OSRepo()
    ingest = IngestFile(db_repo, os_repo)
    inputs = ingest.Inputs(
        dataset=dataset,
        file=file,
        uid=user.uid,
        checksum=checksum,
    )
    outputs = await ingest(inputs)
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


def download_dataset(id, file, user):
    db_repo = DBRepo()
    os_repo = OSRepo()
    retrieve = DownloadDataset(db_repo, os_repo)
    inputs = retrieve.Inputs(id=id, file=file, uid=user.uid)
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


def generate_upload_id(user, checksum, name, dataset):
    db_repo = DBRepo()
    os_repo = OSRepo()
    s3_repo = S3Repo()
    generate = GenerateUploadId(db_repo, os_repo, s3_repo)
    inputs = generate.Inputs(
        uid=user.uid,
        checksum=checksum,
        name=name,
        dataset=dataset,
    )
    outputs = generate(inputs)
    return outputs.upload_id, outputs.parts


def ingest_dataset_chunk(chunk, part_number, upload_id, checksum, user):
    os_repo = OSRepo()
    s3_repo = S3Repo()
    db_repo = DBRepo()
    ingest = IngestDatasetChunk(os_repo, s3_repo, db_repo)
    inputs = ingest.Inputs(
        chunk=chunk,
        uid=user.uid,
        upload_id=upload_id,
        part_number=part_number,
        checksum=checksum,
    )
    outputs = ingest(inputs)
    return outputs.message


async def complete_multipart_upload(user, upload_id):
    db_repo = DBRepo()
    os_repo = OSRepo()
    s3_repo = S3Repo()
    complete = CompleteMultipartUpload(db_repo, os_repo, s3_repo)
    inputs = complete.Inputs(
        uid=user.uid,
        upload_id=upload_id,
    )
    outputs = await complete(inputs)
    return outputs.dataset


async def update_dataset(
    dataset_id, user, name, author, link, license, tags, description
):
    db_repo = DBRepo()
    ingest = UpdateDataset(db_repo)
    inputs = ingest.Inputs(
        uid=user.uid,
        dataset_id=dataset_id,
        name=name,
        description=description,
        author=author,
        link=link,
        license=license,
        tags=tags,
    )
    outputs = await ingest(inputs)
    return outputs.dataset
