from glob import glob
from pathlib import Path
import geopandas as gpd
import os
import pystac
from tqdm import tqdm
import stac_geoparquet
import frontmatter
import random
import pandas as pd
from datetime import datetime
from shapely.geometry import Polygon

from ..auth import with_auth
from ..files.metadata import Metadata
from ..repos import FilesAPIRepo
from ..shared import calculate_checksum

def fix_timestamp(item, field='created'):
	if 'properties' in item.to_dict() and field in item.to_dict()['properties']:
		created = item.to_dict()['properties'][field]
		if isinstance(created, str):
			# Parse and reformat the timestamp to ensure it's compatible with parquet
			try:
				# Parse the timestamp string
				dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
				# Reformat to ISO format without microseconds if they cause issues
				formatted_created = dt.strftime('%Y-%m-%dT%H:%M:%S+00:00')
				item.properties[field] = formatted_created
			except Exception as e:
				print(f"Warning: Could not parse timestamp {created}: {e}")
				# Remove problematic timestamp if parsing fails
				item.properties.pop(field, None)
	return item

def prep_ingest_folder(
	folder,
	verbose=False,
	logger=print,
	force_metadata_update=False,
	sync_metadata=False,
):
	logger("Ingesting directory: " + str(folder))
	catalog_path = folder.joinpath("catalog.parquet")
	files = glob(str(folder) + '/**/*', recursive=True)
	# remove catalog.parquet from files
	files = [f for f in files if f != str(catalog_path)]
	# ingest geometry from files (if tifs) or additional list of geometries
	# https://stac-utils.github.io/stac-geoparquet/latest/spec/stac-geoparquet-spec/#use-cases
	data = []
	for file in tqdm(files, total=len(files), desc="Preparing files"):
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
	print("Reading STAC catalog...", end="", flush=True)
	catalog = pystac.Catalog.from_file(stac_catalog)
	print("done")
	# make all items paths hredf in assets absolute
	catalog.make_all_asset_hrefs_absolute() 
	# generate list of items for all collections
	print(f"Found {len(list(catalog.get_collections()))} collections")
	items = []
	for collection in catalog.get_collections():
		print(f"Preparing items from collection {collection.id}", flush=True)
		# iterate over items
		for item in tqdm(collection.get_items(), total=len(list(collection.get_items()))):
			assert isinstance(item, pystac.Item)
			# Process each asset in the item
			for asset in item.assets.values():
				if not asset.href.startswith(('http://', 'https://')):
					# Asset is a local file
					file_path = Path(asset.href)
					# Calculate and add file size
					asset.extra_fields['size'] = file_path.stat().st_size
					# Calculate and add checksum
					asset.extra_fields['checksum'] = calculate_checksum(str(file_path))
					# print(asset.to_dict())
			# Fix timestamp format in properties.created (did this to solve errors with charter challenge... but I guess people should fix their STAC metadata)
			item = fix_timestamp(item, 'created')
			item = fix_timestamp(item, 'updated')
			items.append(item)
	# save parquet file
	print("Saving parquet file...", end="", flush=True)
	try:
		record_batch_reader = stac_geoparquet.arrow.parse_stac_items_to_arrow(items)
		output_path = stac_catalog.parent / "catalog.parquet"
		stac_geoparquet.arrow.to_parquet(record_batch_reader, output_path)
		print("done")
		return output_path
	except Exception as e:
		print(f"\nError saving parquet file: {e}")
		raise e

def ingest_virtual( # could work for a list of paths with minimal changes...
	path,
	links,
	repo,
	retrieve,
	mode,
	metadata = None, 
	logger=print,
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
	return ingest(path, repo, retrieve, mode, private=False)

def ingest_catalog(path, repo, retrieve, mode):
	return ingest(path, repo, retrieve, mode, private=False)

@with_auth
def ingest(path, repo, retrieve, mode, private, user):
	try:
		readme = frontmatter.load(path.joinpath("README.md"))
		metadata_dict = readme.metadata
		# Add description from content before creating Metadata object
		metadata_dict["description"] = readme.content
		metadata = Metadata(**metadata_dict)
	except Exception as e:
		print(str(e))
		raise Exception("Error loading metadata")
	# retrieve dataset (create if doesn't exist)
	dataset_or_model = retrieve(metadata, user, private)
	current_version = sorted([v['version_id'] for v in dataset_or_model["versions"]])[-1]
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
	catalog_url = files_repo.generate_presigned_url(f'catalog.v{current_version}.parquet', dataset_or_model['id'], user, endpoint=mode)
	# first time ingesting
	if catalog_url is None:
		total_size = 0
		for row in tqdm(gdf.iterrows(), total=len(gdf), desc="Ingesting files"):
			try:
				assets_count = len(row[1]["assets"])
				for k, v in row[1]["assets"].items():
					if not v: continue # skip empty assets
					if v["href"].startswith("http"): continue
					item_id = row[1]["id"]
					# Determine file name based on number of assets
					if assets_count == 1:
						file_name = item_id
					else:
						file_name = f"{item_id}_{k}"
					# print(f"Ingesting file {v['href']} with id {file_name}")
					data, error = files_repo.ingest_file(
						v["href"],
						file_name, 
						# Path(v["href"]).stat().st_size,
						dataset_or_model['id'],
						user,
						mode,
					)
					if error:
						raise Exception(error)
					file_url = f"{repo.url}{mode}/{dataset_or_model['id']}/stage/{file_name}"
					gdf.loc[row[0], "assets"][k]["href"] = file_url
					total_size += v["size"]
			except Exception as e:
				print(f"Error uploading asset {row[0]}: {e}")
				break
		gdf.to_parquet(catalog_path)
		files_repo.ingest_file(str(catalog_path), f'catalog.v{current_version}.parquet', dataset_or_model['id'], user, mode)
		data, error = repo.complete_ingestion(dataset_or_model['id'], current_version, total_size, user)
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
			item_id = row[1]["id"]
			# check if item exists in previous versions
			df = pd.read_parquet(
				path=catalog_url,
				filters=[('id', '=', item_id)]
			)
			exists = len(df) > 0
			updated = False
			assets_count = len(row[1]["assets"])
			for k, v in row[1]["assets"].items():
				if not v: continue # skip empty assets
				if v["href"].startswith("http"): continue
				if assets_count == 1:
					file_name = item_id
				else:
					file_name = f"{item_id}_{k}"
				if exists:
					if df.iloc[0]['assets'][k]["checksum"] == v["checksum"]: # file is the same
						# still need to update the required fields
						# file_url = f"{repo.url}{mode}/{dataset_or_model['id']}/stage/{file_name}"
						file_url = df.iloc[0]['assets'][k]["href"] # keep previous file url to avoid overwriting
						gdf.loc[row[0], "assets"][k]["href"] = file_url
						total_size += v["size"]
						continue
					else: # file is different, so ingest new version but with a different name
						file_name = file_name + f"-{random.randint(1, 1000000)}"
				updated = True
				new_version = True
				num_changes += 1
				# ingest new files
				data, error = files_repo.ingest_file(
					v["href"],
					file_name, # file_name, will be path in local or given id in STAC. if not unique, will overwrite previous file in storage
					# Path(v["href"]).stat().st_size,
					dataset_or_model['id'],
					user,
					# calculate_checksum(asset["href"]),  # is always absolute?
					mode,
					# version,
				)
				if error:
					raise Exception(error)
				file_url = f"{repo.url}{mode}/{dataset_or_model['id']}/stage/{file_name}"
				gdf.loc[row[0], "assets"][k]["href"] = file_url
				total_size += v["size"]
			# if exists and updated:
			# 	if assets_count == 1:
			# 		item_id = file_name
			# 	else:
			# 		item_id = item_id + f"-{random.randint(1, 1000000)}"
			# 	gdf.loc[row[0], "id"] = item_id
		except Exception as e:
			print(f"Error uploading asset {row[0]}: {e}")
			break
	
	# check for deleted files
	df = pd.read_parquet(catalog_url)
	rows_to_remove = df[~df['id'].isin(gdf['id'])]
	if len(rows_to_remove) > 0:
		ids_to_remove = rows_to_remove['id'].values
		gdf = gdf[~gdf['id'].isin(ids_to_remove)]
		new_version = True
		num_changes += len(ids_to_remove)
	
	if not new_version:
		print("No new version was created, your dataset has not changed.")
	else:
		new_version = current_version + 1
		print("A new version was created, your dataset has changed.")
		print(f"Num changes: {num_changes}")
		gdf.to_parquet(catalog_path)
		files_repo.ingest_file(str(catalog_path), f'catalog.v{new_version}.parquet', dataset_or_model['id'], user, mode)
		data, error = repo.complete_ingestion(dataset_or_model['id'], new_version, total_size, user)
		if error:
			raise Exception(error)
		return catalog_path

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