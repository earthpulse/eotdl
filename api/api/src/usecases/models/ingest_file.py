from datetime import datetime
import zipfile
import io
import os

from .retrieve_model import retrieve_owned_model
from ...errors import ModelVersionDoesNotExistError
from ...repos import ModelsDBRepo
from ..files import ingest_file, ingest_existing_file


async def ingest_model_files_batch(batch, model_id, checksums, user, version):
    model = retrieve_owned_model(model_id, user.uid)
    versions = [v.version_id for v in model.versions]
    if not version in versions:
        raise ModelVersionDoesNotExistError()
    # Decompress the received zip file
    tmp_path = f"/tmp/{user.uid}/{model_id}/{version}"
    os.makedirs(tmp_path, exist_ok=True)
    batch_size = 0
    with zipfile.ZipFile(io.BytesIO(await batch.read()), "r") as zf:
        zf.extractall(tmp_path)
    # ingest files
    for file, checksum in zip(zf.namelist(), checksums):
        path = os.path.join(tmp_path, file)
        file_size = await ingest_file(
            file,
            path,
            version,
            model_id,
            checksum,
            model.files,
        )
        batch_size += file_size
    version = [v for v in model.versions if v.version_id == version][0]
    version.size += batch_size  # for Q0+ will add, so put to 0 before if necessary
    model.updatedAt = datetime.now()
    model_db_repo = ModelsDBRepo()
    model_db_repo.update_model(model.id, model.dict())
    return model.id, model.name, zf.namelist()


def add_files_batch_to_model_version(filenames, checksums, model_id, version, user):
    model = retrieve_owned_model(model_id, user.uid)
    versions = [v.version_id for v in model.versions]
    if not version in versions:
        raise ModelVersionDoesNotExistError()
    batch_size = 0
    for filename, checksum in zip(filenames, checksums):
        file_size = ingest_existing_file(
            filename,
            checksum,
            version,
            model.files,
            model_id,
            model.quality,
        )
        batch_size += file_size
    version = [v for v in model.versions if v.version_id == version][0]
    version.size += batch_size  # for Q0+ will add, so put to 0 before if necessary
    model.updatedAt = datetime.now()
    model_db_repo = ModelsDBRepo()
    model_db_repo.update_model(model.id, model.dict())
    return model.id, model.name, filenames


# async def ingest_model_file(file, model_id, version, parent, checksum, user):
#     model = retrieve_owned_model(model_id, user.uid)
#     versions = [v.version_id for v in model.versions]
#     if not version in versions:
#         raise modelVersionDoesNotExistError()
#     filename, file_size = await ingest_file(
#         file, version, parent, model_id, checksum, model.quality, model.files
#     )
#     version = [v for v in model.versions if v.version_id == version][0]
#     version.size += file_size  # for Q0+ will add, so put to 0 before if necessary
#     model.updatedAt = datetime.now()
#     model_db_repo = modelsDBRepo()
#     model_db_repo.update_model(model.id, model.dict())
#     return model.id, model.name, filename


def ingest_file_url():
    # TODO
    return
    # def get_file_name(self, file):
    #     return file.split("/")[-1]

    # def persist_file(self, file, model_id, filename):
    #     return os_repo.persist_file_url(file, model_id, filename)


def ingest_stac():
    # TODO
    return
    # # check if model exists
    # data = db_repo.retrieve("models", model)
    # if not data:
    #     raise modelDoesNotExistError()
    # model = STACmodel(**data)
    # # check user owns model
    # if model.uid != user.uid:
    #     raise modelDoesNotExistError()
    # # TODO: check all assets exist in os
    # # ingest to geodb
    # credentials = retrieve_user_credentials(user)
    # geodb_repo = geodb_repo(credentials)
    # catalog = geodb_repo.insert(model, stac)
    # # the catalog should contain all the info we want to show in the UI
    # model.catalog = catalog
    # keys = list(catalog.keys())
    # if "ml-model:name" in keys:
    #     model.quality = 2
    #     # TODO: compute and report automatic qa metrics
    # # TODO: validate Q2 model, not only check name
    # # TODO: validate Q1 model with required fields/extensions (author, license)
    # db_repo.update("models", model, model.model_dump())
    # return Outputs(model=model)
