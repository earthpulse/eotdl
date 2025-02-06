from pathlib import Path
import frontmatter
from glob import glob
import stac_geoparquet
import pandas as pd
import geopandas as gpd
import os
from shapely.geometry import Polygon
from tqdm import tqdm
from io import BytesIO
import pystac
import stac_geoparquet
from datetime import datetime
# import pyarrow.parquet as pq
import random
import shutil

# import yaml
# import json

from ..auth import with_auth
from ..repos import DatasetsAPIRepo, FilesAPIRepo
from ..shared import calculate_checksum
# from ..files import ingest_files, create_new_version
# # from ..curation.stac import STACDataFrame
# # from .update import update_dataset
# # from .metadata import generate_metadata

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
	if "catalog.json" in [f.name for f in path.iterdir()]:
		prep_ingest_stac(path, logger)
	else:
		prep_ingest_folder(path, verbose, logger, force_metadata_update, sync_metadata)
	return ingest(path)


@with_auth
def ingest(path, user):
	try:
		readme = frontmatter.load(path.joinpath("README.md"))
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
	current_version = sorted([v['version_id'] for v in dataset["versions"]])[-1]
	print("current version: ", current_version)

	# TODO: update README if metadata changed in UI (db)
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

	catalog_path = path.joinpath("catalog.parquet")
	gdf = gpd.read_parquet(catalog_path)
	files_repo = FilesAPIRepo()
	catalog_url = files_repo.generate_presigned_url(f'catalog.v{current_version}.parquet', dataset['id'], user)

	# first time ingesting
	if catalog_url is None:
		total_size = 0
		for row in tqdm(gdf.iterrows(), total=len(gdf), desc="Ingesting files"):
			try:
				for k, v in row[1]["assets"].items():
					if v["href"].startswith("http"): continue
					item_id = row[1]["id"]
					data, error = files_repo.ingest_file(
						v["href"],
						item_id, 
						# Path(v["href"]).stat().st_size,
						dataset['id'],
						user,
						"datasets",
					)
					if error:
						raise Exception(error)
					file_url = f"{repo.url}datasets/{dataset['id']}/stage/{item_id}"
					gdf.loc[row[0], "assets"][k]["href"] = file_url
					total_size += v["size"]
			except Exception as e:
				print(f"Error uploading asset {row[0]}: {e}")
				break
		gdf.to_parquet(catalog_path)
		files_repo.ingest_file(str(catalog_path), f'catalog.v{current_version}.parquet', dataset['id'], user, "datasets")
		data, error = repo.complete_ingestion(dataset['id'], current_version, total_size, user)
		if error:
			raise Exception(error)
		return catalog_path
	
	# files were already ingested
	# TODO: check for deleted files (currently only updating existing files and ingesting new ones)
	# TODO: adding new links in virtual datasets dont trigger new version (but changing README does)
	new_version = False
	num_changes = 0
	total_size = 0
	for row in tqdm(gdf.iterrows(), total=len(gdf), desc="Ingesting files"):
		try:
			for k, v in row[1]["assets"].items():
				if v["href"].startswith("http"): continue
				item_id = row[1]["id"]
				# check if file exists in previous versions
				df = pd.read_parquet(
					path=catalog_url,
					filters=[('id', '=', item_id)]
				)
				if len(df) > 0: # file exists in previous versions
					if df.iloc[0]['assets'][k]["checksum"] == v["checksum"]: # file is the same
						# still need to update the required fields
						file_url = f"{repo.url}datasets/{dataset['id']}/stage/{item_id}"
						gdf.loc[row[0], "assets"][k]["href"] = file_url
						total_size += v["size"]
						continue
					else: # file is different, so ingest new version but with a different id
						item_id = item_id + f"-{random.randint(1, 1000000)}"
						gdf.loc[row[0], "id"] = item_id
				new_version = True
				num_changes += 1
				# ingest new files
				data, error = files_repo.ingest_file(
					v["href"],
					item_id, # item id, will be path in local or given id in STAC. if not unique, will overwrite previous file in storage
					# Path(v["href"]).stat().st_size,
					dataset['id'],
					user,
					# calculate_checksum(asset["href"]),  # is always absolute?
					"datasets",
					# version,
				)
				if error:
					raise Exception(error)
				file_url = f"{repo.url}datasets/{dataset['id']}/stage/{item_id}"
				gdf.loc[row[0], "assets"][k]["href"] = file_url
				total_size += v["size"]
		except Exception as e:
			print(f"Error uploading asset {row[0]}: {e}")
			break
	if not new_version:
		print("No new version was created, your dataset has not changed.")
	else:
		new_version = current_version + 1
		print("A new version was created, your dataset has changed.")
		print(f"Num changes: {num_changes}")
		gdf.to_parquet(catalog_path)
		files_repo.ingest_file(str(catalog_path), f'catalog.v{new_version}.parquet', dataset['id'], user, "datasets")
		# TODO: ingest README.md
		data, error = repo.complete_ingestion(dataset['id'], new_version, total_size, user)
		if error:
			raise Exception(error)
		return catalog_path

def prep_ingest_folder(
	folder,
	verbose=False,
	logger=print,
	force_metadata_update=False,
	sync_metadata=False,
):
	logger("Ingesting directory: " + str(folder))
	catalog_path = folder.joinpath("catalog.parquet")
	# catalog_path.touch()
	files = glob(str(folder) + '/**/*', recursive=True)
	# remove catalog.parquet from files
	files = [f for f in files if f != str(catalog_path)]
	# ingest geometry from files (if tifs) or additional list of geometries
	# https://stac-utils.github.io/stac-geoparquet/latest/spec/stac-geoparquet-spec/#use-cases
	data = []
	for file in files:
		file_path = Path(file)
		if file_path.is_file():
			relative_path = os.path.relpath(file_path, catalog_path.parent)
			absolute_path = str(file_path)
			# THIS IS THE MINIMUM REQUIRED FIELDS TO CREATE A VALID STAC ITEM
			data.append(create_stac_item(relative_path, absolute_path))
	gdf = gpd.GeoDataFrame(data, geometry='geometry')
	# Save to parquet
	gdf.to_parquet(catalog_path)
	return catalog_path

# IF THE KEYS IN THE ASSETS ARE NOT THE SAME ON ALL ITEMS, THE PARQUET WILL NOT BE VALID !!!
def prep_ingest_stac(path, logger=None): # in theory should work with a remote catalog (given URL)
	# read stac catalog
	stac_catalog = path / "catalog.json"
	catalog = pystac.Catalog.from_file(stac_catalog)
	# make all items paths hredf in assets absolute
	catalog.make_all_asset_hrefs_absolute() 
	# generate list of items for all collections
	items = []
	for collection in catalog.get_collections():
		# iterate over items
		for item in tqdm(collection.get_items(), desc=f"Ingesting items from collection {collection.id}"):
			assert isinstance(item, pystac.Item)
			items.append(item)
	# save parquet file
	record_batch_reader = stac_geoparquet.arrow.parse_stac_items_to_arrow(items)
	output_path = stac_catalog.parent / "catalog.parquet"
	stac_geoparquet.arrow.to_parquet(record_batch_reader, output_path)
	return output_path

@with_auth
def ingest_virutal_dataset( # could work for a list of paths with minimal changes...
	path,
	links,
	metadata = None, 
	logger=print,
	user=None,
):
	path = Path(path)
	if metadata is None:
		readme = frontmatter.load(path.joinpath("README.md"))
		metadata_dict = readme.metadata
		# Add description from content before creating Metadata object
		metadata_dict["description"] = readme.content
		metadata = Metadata(**metadata_dict)
	else:
		metadata = Metadata(**metadata)
		metadata.save_metadata(path)
	data = []
	for link in links:
		assert link.startswith("http"), "All links must start with http or https"
		data.append(create_stac_item(link, link))
	data.append(create_stac_item('README.md', str(path / "README.md")))
	gdf = gpd.GeoDataFrame(data, geometry='geometry')
	gdf.to_parquet(path / "catalog.parquet")
	return ingest(path)

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

def create_stac_item(item_id, asset_href):
	return {
		'type': 'Feature',
		'stac_version': '1.0.0',
		'stac_extensions': [],
		'datetime': datetime.now(),  # must be native timestamp (https://github.com/apache/parquet-format/blob/master/LogicalTypes.md#timestamp)
		'id': item_id,
		'bbox': {
			'xmin': 0.0,
			'ymin': 0.0,
			'xmax': 0.0,
			'ymax': 0.0
		}, # infer from file or from list of geometries
		'geometry': Polygon(), # empty polygon
		'assets': { 'asset': { # STAC needs this to be a Dict[str, Asset], not list !!! use same key or parquet breaks !!!
			'href': asset_href,
			'checksum': calculate_checksum(asset_href) if not asset_href.startswith("http") else None,
			'timestamp': datetime.now(),
			'size': Path(asset_href).stat().st_size if not asset_href.startswith("http") else None,
		}},
		"links": [],
		# 'collection': 'source',
		# anything below are properties (need at least one!)
		'repository': 'eotdl',				
	}
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


