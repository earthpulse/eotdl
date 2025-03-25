from pathlib import Path

from ..repos import DatasetsAPIRepo
from ..files.ingest import prep_ingest_stac, prep_ingest_folder, ingest

def retrieve_dataset(metadata, user):
	repo = DatasetsAPIRepo()
	data, error = repo.retrieve_dataset(metadata.name)
	# print(data, error)
	if data and data["uid"] != user["uid"]:
		raise Exception("Dataset already exists.")
	if error and error == "Dataset doesn't exist":
		# create dataset
		data, error = repo.create_dataset(metadata.dict(), user)
		# print(data, error)
		if error:
			raise Exception(error)
	return data

def ingest_dataset(
	path,
	verbose=False,
	logger=print,
	force_metadata_update=False,
	sync_metadata=False,
):
	path = Path(path)
	if not path.is_dir():
		raise Exception("Path must be a folder")
	if "catalog.json" in [f.name for f in path.iterdir()]:
		prep_ingest_stac(path, logger)
	else:
		prep_ingest_folder(path, verbose, logger, force_metadata_update, sync_metadata)
	return ingest(path, DatasetsAPIRepo(), retrieve_dataset, 'datasets')


