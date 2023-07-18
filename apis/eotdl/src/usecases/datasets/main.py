from ...repos import DBRepo, OSRepo, S3Repo  # , GeoDBRepo
from .CreateDataset import CreateDataset
from .IngestFile import IngestFile
from .IngestFileURL import IngestFileURL
from .UpdateDataset import UpdateDataset
from .RetrieveDatasets import RetrieveDatasets
from .RetrieveOneDatasetByName import RetrieveOneDatasetByName
from .DownloadDataset import DownloadDataset
from .RetrieveDatasetsLeaderboard import RetrieveDatasetsLeaderboard
from ..tags import retrieve_tags
from .LikeDataset import LikeDataset
from .RetrieveLikedDatasets import RetrieveLikedDatasets
from .RetrievePopularDatasets import RetrievePopularDatasets
from .IngestDatasetChunk import IngestDatasetChunk
from .DeleteDataset import DeleteDataset
from .GenerateUploadId import GenerateUploadId
from .CompleteMultipartUpload import CompleteMultipartUpload
from .IngestQ1Dataset import IngestQ1Dataset
from .IngestSTAC import IngestSTAC
from .DownloadDatasetSTAC import DownloadDatasetSTAC
from .DeleteDatasetFile import DeleteDatasetFile


def create_dataset(user, name, authors, source, license):
    db_repo = DBRepo()
    create = CreateDataset(db_repo)
    inputs = CreateDataset.Inputs(
        uid=user.uid, name=name, authors=authors, source=source, license=license
    )
    outputs = create(inputs)
    return outputs.dataset_id


async def ingest_file(file, dataset_id, checksum, user):
    db_repo = DBRepo()
    os_repo = OSRepo()
    ingest = IngestFile(db_repo, os_repo)
    inputs = ingest.Inputs(
        dataset_id=dataset_id,
        file=file,
        uid=user.uid,
        checksum=checksum,
    )
    outputs = await ingest(inputs)
    return outputs.dataset_id, outputs.dataset_name, outputs.file_name


async def ingest_file_url(file, dataset, user):
    db_repo, os_repo = DBRepo(), OSRepo()
    ingest = IngestFileURL(db_repo, os_repo)
    inputs = ingest.Inputs(
        dataset=dataset,
        file=file,
        uid=user.uid,
    )
    outputs = await ingest(inputs)
    return outputs.dataset_id, outputs.dataset_name, outputs.file_name


def ingest_stac(stac, dataset, user):
    pass
    # db_repo, os_repo, geodb_repo = DBRepo(), OSRepo(), GeoDBRepo()
    # ingest = IngestSTAC(db_repo, os_repo, geodb_repo)
    # inputs = ingest.Inputs(
    #     dataset=dataset,
    #     stac=stac,
    #     uid=user.uid,
    # )
    # outputs = ingest(inputs)
    # return outputs.dataset


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


def download_stac(dataset_id, user):
    db_repo, geodb_repo = DBRepo(), GeoDBRepo()
    retrieve = DownloadDatasetSTAC(db_repo, geodb_repo)
    inputs = retrieve.Inputs(dataset_id=dataset_id, uid=user.uid)
    outputs = retrieve(inputs)
    return outputs.stac


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


def generate_upload_id(user, checksum, name, dataset_id):
    db_repo = DBRepo()
    os_repo = OSRepo()
    s3_repo = S3Repo()
    generate = GenerateUploadId(db_repo, os_repo, s3_repo)
    inputs = generate.Inputs(
        uid=user.uid,
        checksum=checksum,
        name=name,
        dataset_id=dataset_id,
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


def update_dataset(dataset_id, user, name, author, link, license, tags, description):
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
    outputs = ingest(inputs)
    return outputs.dataset


def ingest_q1_dataset(dataset, uid):
    pass
    # db_repo = DBRepo()
    # geodb_repo = GeoDBRepo()
    # ingest = IngestQ1Dataset(db_repo)
    # inputs = ingest.Inputs(
    #     dataset=dataset,
    #     uid=uid,
    # )
    # outputs = ingest(inputs)
    # return outputs.message


def delete_dataset_file(user, dataset_id, file_name):
    db_repo = DBRepo()
    os_repo = OSRepo()
    delete = DeleteDatasetFile(db_repo, os_repo)
    inputs = delete.Inputs(
        uid=user.uid,
        dataset_id=dataset_id,
        file_name=file_name,
    )
    outputs = delete(inputs)
    return outputs.message
