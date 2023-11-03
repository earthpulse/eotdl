from ...repos import ModelsDBRepo, OSRepo, FilesDBRepo
from .retrieve_model import retrieve_model_by_name


def delete_model(name):
    db_repo, files_repo, os_repo = ModelsDBRepo(), FilesDBRepo(), OSRepo()
    model = retrieve_model_by_name(name)
    for file in files_repo.retrieve_files(model.files)[0]["files"]:
        os_repo.delete(model.id, f"{file['name']}_{file['version']}")
    db_repo.delete_files(model.files)
    db_repo.delete_model(model.id)
    db_repo.decrease_user_model_count(model.uid)
    return "model deleted successfully"
