from pathlib import Path

from ..repos import FEAPIRepo
from ..files.ingest import prep_ingest_folder, ingest

def retrieve_pipeline(metadata, user):
	repo = FEAPIRepo()
	data, error = repo.retrieve_pipeline(metadata.name)
	if data and data["uid"] != user["uid"]:
		raise Exception("Pipeline already exists.")
	if error and error == "Pipeline doesn't exist":
		# create pipeline
		data, error = repo.create_pipeline(metadata.dict(), user)
		# print(data, error)
		if error:
			raise Exception(error)
	return data

def ingest_openeo(
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
	# if "catalog.json" in [f.name for f in path.iterdir()]:
	# 	prep_ingest_stac(path, logger)
	# else:
	# 	prep_ingest_folder(path, verbose, logger, force_metadata_update, sync_metadata)
	prep_ingest_folder(path, verbose, logger, force_metadata_update, sync_metadata)
	return ingest(path, FEAPIRepo(), retrieve_pipeline, 'pipelines', private)


# def ingest_virtual_dataset( # could work for a list of paths with minimal changes...
# 	path,
# 	links,
# 	metadata = None, 
# 	logger=print,
# 	user=None,
# ):
# 	return ingest_virtual(path, links, DatasetsAPIRepo(), retrieve_dataset, 'datasets', metadata, logger)

# def ingest_dataset_catalog(path, logger=None):
# 	path = Path(path)
# 	return ingest_catalog(path, DatasetsAPIRepo(), retrieve_dataset, 'datasets')