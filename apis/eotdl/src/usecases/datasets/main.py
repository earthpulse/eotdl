from ...repos import DBRepo, OSRepo

def ingest_dataset(file, name, user):
	mongo_repo = DBRepo()
	minio_repo = OSRepo()
	return name