import pandas as pd
from minio import Minio
from datetime import datetime
import json
from shapely.geometry import Polygon
import geopandas as gpd
import random
# import rasterio as rio
from dotenv import load_dotenv
import os
load_dotenv()

# load datasets

def parse_with_dates(json_str):
	data = json.loads(json_str)
	# parse dates if needed
	return data

df = pd.read_csv("datasets.csv")

df['versions'] = df['versions'].apply(json.loads)
df['files'] = df['files'].apply(json.loads)
df['folders'] = df['folders'].apply(json.loads)

# generate catalogs

minio_client = Minio(
	endpoint=os.getenv('S3_ENDPOINT'),
	access_key=os.getenv('ACCESS_KEY_ID'),
	secret_key=os.getenv('SECRET_ACCESS_KEY'),
	secure=True,
)

old_bucket = os.getenv('OLD_BUCKET')
new_bucket = os.getenv('NEW_BUCKET')

files_map = []
counter = 1
for row in df.iterrows():
	dataset_id = row[1]['id']
	dataset_name = row[1]['name']
	versions = row[1]['versions']
	files = row[1]['files']
	folders = row[1]['folders']
	print(dataset_name, dataset_id, f"{counter}/{len(df)}")
	counter += 1
	for version in json.loads(versions):
		print(version)
		data = []
		print("found", len(json.loads(files)), "files")
		for file in json.loads(files):
			if not version['version_id'] in file['versions']:
				continue
			# print(file)
			item_id = file['name']
			print(file['name'])
			if file['version'] > 1:
					item_id = f'{file["name"]}-{random.randint(1, 1000000)}'
					print(file['name'], '->', item_id)
			stac_item  = {
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
					'href': f'https://dev.api.eotdl.com/datasets/{dataset_id}/stage/{item_id}', # TODO: change to prod
					'checksum': file['checksum'],
					'timestamp': file['createdAt'],
					'size': file['size'],
				}},
				"links": [],
				# 'collection': 'source',
				# anything below are properties (need at least one!)
				'repository': 'eotdl',				
			}
			# TODO in the future if we want. Check if file is a tif/tiff
			# if file['name'].lower().endswith(('.tif', '.tiff')):
			# 	try:
			# 		# Get presigned URL for reading file
			# 		presigned_url = minio_client.get_presigned_url(
			# 			"GET",
			# 			old_bucket,
			# 			f'{dataset_id}/{file["name"]}_{file["version"]}'
			# 		)
			# 		# Read with rasterio using presigned URL
			# 		with rio.open(presigned_url) as src:
			# 			bounds = src.bounds
			# 			stac_item['bbox'] = {
			# 				'xmin': bounds.left,
			# 				'ymin': bounds.bottom, 
			# 				'xmax': bounds.right,
			# 				'ymax': bounds.top
			# 			}
			# 			stac_item['geometry'] = Polygon([
			# 				[bounds.left, bounds.bottom],
			# 				[bounds.left, bounds.top],
			# 				[bounds.right, bounds.top], 
			# 				[bounds.right, bounds.bottom],
			# 				[bounds.left, bounds.bottom]
			# 			])
			# 	except:
			# 		# If reading fails, keep empty bbox/geometry
			# 		pass
			data.append(stac_item)
			# copy file from old bucket to new bucket
			# minio_client.fget_object(
			# 	old_bucket,
			# 	f'{dataset_id}/{file['name']}_{file['version']}',
			# 	f'{dataset_id}/{item_id}'
			# )
			# minio_client.fput_object(
			# 	new_bucket,
			# 	f'{dataset_id}/{item_id}',
			# 	f'{dataset_id}/{item_id}'
			# )
			files_map.append((f'{dataset_id}/{file['name']}_{file['version']}', f'{dataset_id}/{item_id}'))
		if data:
			gdf = gpd.GeoDataFrame(data, geometry='geometry')
			catalog_name = f'catalog.v{version["version_id"]}.parquet'
			gdf.to_parquet(catalog_name)
			# copy parquet to bucket
			minio_client.fput_object(
				new_bucket,
				f'{dataset_id}/{catalog_name}',
				catalog_name
			)
			print("copied", catalog_name)
	
_df = pd.DataFrame(files_map, columns=['old_path', 'new_path'])
_df.to_csv('files_map.csv', index=False)