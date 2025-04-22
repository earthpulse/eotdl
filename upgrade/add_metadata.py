from dotenv import load_dotenv
import os
import geopandas as gpd
from minio import Minio
import hashlib
import requests
from datetime import datetime
from shapely.geometry import Polygon
from minio.commonconfig import REPLACE, CopySource
from tqdm import tqdm

load_dotenv()

minio_client = Minio(
	endpoint=os.getenv('S3_ENDPOINT'),
	access_key=os.getenv('ACCESS_KEY_ID'),
	secret_key=os.getenv('SECRET_ACCESS_KEY'),
	secure=True,
)

bucket = os.getenv('BUCKET')

def calculate_checksum(file_path):
    sha1_hash = hashlib.sha1()
    response = requests.get(file_path, stream=True)
    for chunk in response.iter_content(chunk_size=4096):
        if chunk:
            sha1_hash.update(chunk)
    return sha1_hash.hexdigest()


# list files in bucket

dataset_id = "67d1a13482ec193cb1942a4b"

files = list(minio_client.list_objects(bucket, prefix=dataset_id, recursive=True))

size = 0
count = 1
data = []
for file in tqdm(files):
	# print(file.object_name)
	stats = minio_client.stat_object(bucket, file.object_name)
	size += stats.size
	
	if file.object_name.endswith('_1'):
		print(file.object_name)
		break
		# try:
		# 	new_name = file.object_name[:-2]
		# 	stats = minio_client.stat_object(bucket, new_name)
		# 	size += stats.size
		# 	minio_client.remove_object(bucket, file.object_name)
		# except:
		# 	# print(f"Renaming {file.object_name} to {new_name}")
		# 	# Copy object with new name
		# 	# minio_client.copy_object(bucket, new_name, CopySource(bucket, file.object_name) )
		# 	print(f"{new_name} not found")

	item_id = file.object_name.split(f'{dataset_id}/')[-1]
	presigned_url = minio_client.presigned_get_object(bucket, file.object_name)
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
			'href': f'https://api.eotdl.com/models/{dataset_id}/stage/{item_id}', 
			'checksum': calculate_checksum(presigned_url),
			'timestamp': datetime.now(),
			'size': stats.size,
		}},
		"links": [],
		# 'collection': 'source',
		# anything below are properties (need at least one!)
		'repository': 'eotdl',				
	}
	data.append(stac_item)

	count += 1

	# if count > 10:
	# 	break

gdf = gpd.GeoDataFrame(data, geometry='geometry')
catalog_name = f'catalog.v1.parquet'
gdf.to_parquet(catalog_name)
minio_client.fput_object(bucket, f"{dataset_id}/catalog.v1.parquet", catalog_name)

print(size)