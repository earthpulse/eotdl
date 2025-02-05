from pathlib import Path
import frontmatter
from glob import glob
import stac_geoparquet
import pandas as pd
import geopandas as gpd
import os
from shapely.geometry import Polygon
from tqdm import tqdm

# import yaml
# import json
# import pystac

from ..auth import with_auth
from ..repos import DatasetsAPIRepo, FilesAPIRepo
from ..shared import calculate_checksum
# from ..files import ingest_files, create_new_version
# # from ..curation.stac import STACDataFrame
# # from .update import update_dataset
# # from .metadata import generate_metadata

from ..curation.stac import create_stac_items_from_folder
from ..models import Metadata


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
	# if "catalog.json" in [f.name for f in path.iterdir()]:
	#     return ingest_stac(path / "catalog.json", logger)
	return ingest_folder(path, verbose, logger, force_metadata_update, sync_metadata)


@with_auth
def ingest_folder(
	folder,
	verbose=False,
	logger=print,
	force_metadata_update=False,
	sync_metadata=False,
	user=None,
):
	try:
		readme = frontmatter.load(folder.joinpath("README.md"))
		metadata_dict = readme.metadata
		# Add description from content before creating Metadata object
		metadata_dict["description"] = readme.content
		metadata = Metadata(**metadata_dict)
	except Exception as e:
		print(str(e))
		raise Exception("Error loading metadata")

	repo = DatasetsAPIRepo()
	# retrieve dataset (create if doesn't exist)
	dataset = retrieve_dataset(metadata, user)
	# update_metadata = True
	# if "description" in dataset:
	#     # do not do this if the dataset is new, only if it already exists
	#     update_metadata = check_metadata(
	#         dataset, metadata, content, force_metadata_update, sync_metadata, folder
	#     )
	# if update_metadata:
	#     update_dataset(dataset["id"], metadata, content, user)
	# return ingest_files(
	#     repo, dataset["id"], folder, verbose, logger, user, endpoint="datasets"
	# )

	print("Ingesting directory: ", folder)
	catalog_path = folder.joinpath("catalog.parquet")
	catalog_path.touch()

	files = glob(str(folder) + '/**/*', recursive=True)

	# ingest geometry from files (if tifs) or additional list of geometries
	# https://stac-utils.github.io/stac-geoparquet/latest/spec/stac-geoparquet-spec/#use-cases
	# TODO: for large datasets, explore pyarrow
	data = []
	for file in files:
		file_path = Path(file)
		if file_path.is_file():
			# file_path = Path(file)
			# item_dir = folder / file_path.name
			# relative_path = Path(os.path.relpath(file_path.name, item_dir))
			relative_path = os.path.relpath(file_path, catalog_path.parent)

			# THIS IS THE MINIMUM REQUIRED FIELDS TO CREATE A VALID STAC ITEM
			data.append({
				'stac_extensions': [],
				'id': relative_path,
				'bbox': {
					'xmin': 0.0,
					'ymin': 0.0,
					'xmax': 0.0,
					'ymax': 0.0
				}, # infer from file or from list of geometries
				'geometry': Polygon(), # empty polygon
				'assets': [{
					# 'href': file,
					'href': relative_path,
					# "checksum": "TODO",
				}],
				"links": [],
				'collection': metadata.name,
				# anything below are properties (need at least one!)
				# 'properties': [],
				'abc': [],
				'123': {
					'asfhjk': [1, 2, 3]
				},
				# '123:asd': [1, 2, 3] # this does not work for deeply nested properties
			})

	gdf = gpd.GeoDataFrame(data, geometry='geometry')

	files_repo = FilesAPIRepo()
	for row in tqdm(gdf.iterrows(), total=len(gdf), desc="Ingesting files"):
		try:
			for i, asset in enumerate(row[1]["assets"]):
				# print(asset['href'])
				file = catalog_path.parent / Path(asset["href"])
				data, error = files_repo.ingest_file(
					str(file),
					asset["href"],
					file.stat().st_size,
					dataset['id'],
					user,
					# calculate_checksum(asset["href"]),  # is always absolute?
					"datasets",
					# version,
				)
				if error:
					raise Exception(error)
				file_url = f"{repo.url}datasets/{dataset['id']}/stage/{asset["href"]}"
				gdf.loc[row[0], "assets"][i]["href"] = file_url
		except Exception as e:
			print(f"Error uploading asset {row[0]}: {e}")
			break

	# Save to parquet
	gdf.to_parquet(catalog_path)
	files_repo.ingest_file(str(catalog_path), "catalog.parquet", catalog_path.stat().st_size, dataset['id'], user, "datasets")

	data, error = repo.complete_ingestion(dataset['id'], user)
	if error:
		raise Exception(error)
	
	return catalog_path



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
		data["id"] = data["dataset_id"]
	return data





# def check_metadata(
#     dataset, metadata, content, force_metadata_update, sync_metadata, folder
# ):
#     if (
#         dataset["name"] != metadata.name
#         or dataset["description"] != content
#         or dataset["authors"] != metadata.authors
#         or dataset["source"] != metadata.source
#         or dataset["license"] != metadata.license
#         or dataset["thumbnail"] != metadata.thumbnail
#     ):
#         if not force_metadata_update and not sync_metadata:
#             raise Exception(
#                 "The provided metadata is not consistent with the current metadata. Use -f to force metadata update or -s to sync your local metadata."
#             )
#         if force_metadata_update:
#             return True
#         if sync_metadata:
#             generate_metadata(str(folder), dataset)
#             return False
#     return False


# def retrieve_stac_dataset(dataset_name, user):
#     repo = DatasetsAPIRepo()
#     data, error = repo.retrieve_dataset(dataset_name)
#     # print(data, error)
#     if data and data["uid"] != user["uid"]:
#         raise Exception("Dataset already exists.")
#     if error and error == "Dataset doesn't exist":
#         # create dataset
#         data, error = repo.create_stac_dataset(dataset_name, user)
#         # print(data, error)
#         if error:
#             raise Exception(error)
#         data["id"] = data["dataset_id"]
#     return data["id"]


# @with_auth
# def ingest_stac(stac_catalog, logger=None, user=None):
#     repo, files_repo = DatasetsAPIRepo(), FilesAPIRepo()
#     # load catalog
#     logger("Loading STAC catalog...")
#     df = STACDataFrame.from_stac_file(stac_catalog) # assets are absolute for file ingestion
#     catalog = df[df["type"] == "Catalog"]
#     assert len(catalog) == 1, "STAC catalog must have exactly one root catalog"
#     dataset_name = catalog.id.iloc[0]
#     # retrieve dataset (create if doesn't exist)
#     dataset_id = retrieve_stac_dataset(dataset_name, user)
#     # create new version
#     version = create_new_version(repo, dataset_id, user)
#     logger("New version created, version: " + str(version))
#     df2 = df.dropna(subset=["assets"])
#     for row in tqdm(df2.iterrows(), total=len(df2)):
#         try:
#             for k, v in row[1]["assets"].items():
#                 data, error = files_repo.ingest_file(
#                     v["href"],
#                     dataset_id,
#                     user,
#                     calculate_checksum(v["href"]),  # is always absolute?
#                     "datasets",
#                     version,
#                 )
#                 if error:
#                     raise Exception(error)
#                 file_url = f"{repo.url}datasets/{data['dataset_id']}/download/{data['filename']}"
#                 df.loc[row[0], "assets"][k]["href"] = file_url
#         except Exception as e:
#             logger(f"Error uploading asset {row[0]}: {e}")
#             break
#     # ingest the STAC catalog into geodb
#     logger("Ingesting STAC catalog...")
#     data, error = repo.ingest_stac(json.loads(df.to_json()), dataset_id, user)
#     if error:
#         # TODO: delete all assets that were uploaded
#         raise Exception(error)
#     logger("Done")
#     return
