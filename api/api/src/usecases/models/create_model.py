from ...models import Model, Files
from ...errors import (
    ModelAlreadyExistsError,
    ModelDoesNotExistError,
)
from ...repos import ModelsDBRepo

from .retrieve_model import retrieve_model_by_name
from ..user import check_user_can_create_model  # , retrieve_user_credentials


def create_model(user, name, authors, source, license):
    repo = ModelsDBRepo()
    try:
        retrieve_model_by_name(name)
        raise ModelAlreadyExistsError()
    except ModelDoesNotExistError:
        check_user_can_create_model(user)
        id, files_id = repo.generate_id(), repo.generate_id()
        files = Files(id=files_id, dataset=id)
        model = Model(
            uid=user.uid,
            id=id,
            files=files_id,
            name=name,
            authors=authors,
            source=source,
            license=license,
        )
        repo.persist_files(files.model_dump(), files.id)
        repo.persist_model(model.model_dump(), model.id)
        repo.increase_user_model_count(user.uid)
        return model.id


# def create_stac_dataset(user, name):
#     repo = ModelsDBRepo()
#     credentials = retrieve_user_credentials(user)
#     geodb_repo = GeoDBRepo(credentials)  # validate credentials
#     try:
#         retrieve_dataset_by_name(name)
#         raise ModelAlreadyExistsError()
#     except ModelDoesNotExistError:
#         check_user_can_create_dataset(user)
#         id = repo.generate_id()
#         # do we manage files as well or delegate to geodb?
#         dataset = STACDataset(
#             uid=user.uid,
#             id=id,
#             name=name,
#         )
#         repo.persist_dataset(dataset.model_dump(), dataset.id)
#         repo.increase_user_dataset_count(user.uid)
#         return dataset.id
