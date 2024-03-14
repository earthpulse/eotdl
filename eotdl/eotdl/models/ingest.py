from pathlib import Path
import yaml
import frontmatter
import markdown

from ..auth import with_auth
from .metadata import Metadata, generate_metadata
from ..repos import ModelsAPIRepo
from ..shared import calculate_checksum
from ..files import ingest_files
from .update import update_model


def ingest_model(
    path, verbose=False, logger=print, force_metadata_update=False, sync_metadata=False
):
    path = Path(path)
    if not path.is_dir():
        raise Exception("Path must be a folder")
    # if "catalog.json" in [f.name for f in path.iterdir()]:
    #     return ingest_stac(path / "catalog.json", logger)
    return ingest_folder(path, verbose, logger, force_metadata_update, sync_metadata)


def retrieve_model(metadata, user):
    repo = ModelsAPIRepo()
    data, error = repo.retrieve_model(metadata.name)
    # print(data, error)
    if data and data["uid"] != user["uid"]:
        raise Exception("Model already exists.")
    if error and error == "Model doesn't exist":
        # create dataset
        data, error = repo.create_model(metadata.dict(), user)
        # print(data, error)
        if error:
            raise Exception(error)
        data["id"] = data["model_id"]
    return data


@with_auth
def ingest_folder(
    folder,
    verbose=False,
    logger=print,
    force_metadata_update=False,
    sync_metadata=False,
    user=None,
):
    repo = ModelsAPIRepo()
    # load metadata
    try:
        readme = frontmatter.load(folder.joinpath("README.md"))
        metadata, content = readme.metadata, readme.content
        metadata = Metadata(**metadata)
    except FileNotFoundError:
        # load metadata (legacy)
        metadata = (
            yaml.safe_load(open(folder.joinpath("metadata.yml"), "r").read()) or {}
        )
        metadata = Metadata(**metadata)
        content = None
    except Exception as e:
        raise Exception("Error loading metadata")
    # retrieve model (create if doesn't exist)
    model = retrieve_model(metadata, user)
    if content:
        content = markdown.markdown(content)
    update_metadata = True
    if "description" in model:
        # do not do this if the model is new, only if it already exists
        update_metadata = check_metadata(
            model, metadata, content, force_metadata_update, sync_metadata, folder
        )
    if update_metadata:
        update_model(model["id"], metadata, content, user)
    # ingest files
    return ingest_files(
        repo, model["id"], folder, verbose, logger, user, endpoint="models"
    )


def check_metadata(
    dataset, metadata, content, force_metadata_update, sync_metadata, folder
):
    if (
        dataset["name"] != metadata.name
        or dataset["description"] != content
        or dataset["authors"] != metadata.authors
        or dataset["source"] != metadata.source
        or dataset["license"] != metadata.license
        or dataset["thumbnail"] != metadata.thumbnail
    ):
        if not force_metadata_update and not sync_metadata:
            raise Exception(
                "The provided metadata is not consistent with the current metadata. Use -f to force metadata update or -s to sync your local metadata."
            )
        if force_metadata_update:
            return True
        if sync_metadata:
            generate_metadata(str(folder), dataset)
            return False
    return False
