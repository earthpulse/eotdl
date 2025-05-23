from pathlib import Path

from ..repos import ModelsAPIRepo
from ..files.ingest import prep_ingest_stac, prep_ingest_folder, ingest, ingest_virtual, ingest_catalog

def retrieve_model(metadata, user, private=False):
	repo = ModelsAPIRepo()
	data, error = repo.retrieve_model(metadata.name)
	# print(data, error)
	if data and data["uid"] != user["uid"]:
		raise Exception("Model already exists.")
	if error and error == "Model doesn't exist":
		# create model
		data, error = repo.create_model(metadata.dict(), user)
		if error:
			raise Exception(error)
	return data

def ingest_model(
	path,
	verbose=False,
	logger=print,
	force_metadata_update=False,
	sync_metadata=False,
	private=False,
):
	path = Path(path)
	if not path.is_dir():
		raise Exception("Path must be a folder")
	if "catalog.json" in [f.name for f in path.iterdir()]:
		prep_ingest_stac(path, logger)
	else:
		prep_ingest_folder(path, verbose, logger, force_metadata_update, sync_metadata)
	return ingest(path, ModelsAPIRepo(), retrieve_model, 'models', private)

def ingest_virtual_model( # could work for a list of paths with minimal changes...
	path,
	links,
	metadata = None, 
	logger=print,
	user=None,
):
	return ingest_virtual(path, links, ModelsAPIRepo(), retrieve_model, 'models', metadata, logger)

def ingest_model_catalog(path, logger=None):
	path = Path(path)
	return ingest_catalog(path, ModelsAPIRepo(), retrieve_model, 'models')