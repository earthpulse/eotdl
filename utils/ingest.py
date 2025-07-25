from minio import Minio
import dotenv
import os
from glob import glob
from tqdm import tqdm
from pathlib import Path
from datetime import datetime
from shapely.geometry import Polygon
from pathlib import Path
import hashlib
import geopandas as gpd

dotenv.load_dotenv()

client = Minio(
	endpoint=os.environ['S3_ENDPOINT'],
	access_key=os.environ['ACCESS_KEY_ID'],
	secret_key=os.environ['SECRET_ACCESS_KEY'],
	secure=True,
)

dataset_id = "687b5f9825bb57c11769bb8d"
path = "/fastdata/charter-full-dataset/"

files = glob(path + '**/*', recursive=True)

print("uploading files...", flush=True)
for file in tqdm(files):
    if os.path.isdir(file): continue
    object_name = dataset_id + '/' + file.replace(path, '')
    # stats = client.stat_object(os.environ['BUCKET'], object_name)
    # if stats: continue
    client.fput_object(
        os.environ['BUCKET'],
        object_name,
        file,
    )
print("done")

def calculate_checksum(file_path):
    sha1_hash = hashlib.sha1()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            sha1_hash.update(chunk)
    return sha1_hash.hexdigest()

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
		}, 
		'geometry': Polygon(), # empty polygon
		'assets': { 'asset': { 
			'href': asset_href,
			'checksum': calculate_checksum(asset_href),
			'timestamp': datetime.now(),
			'size': Path(asset_href).stat().st_size,
		}},
		"links": [],
		# 'collection': 'source',
		# anything below are properties (need at least one!)
		'repository': 'eotdl',				
	}

print("creating catalog...", flush=True)
catalog_path = Path(path + "catalog.parquet")
files = [f for f in files if f != str(catalog_path)]
data = []
for file in tqdm(files):
    file_path = Path(file)
    if file_path.is_file():
        relative_path = os.path.relpath(file_path, catalog_path.parent)
        absolute_path = str(file_path)
        stac_item = create_stac_item(relative_path, absolute_path)
        stac_item['assets']['asset']['href'] = f"https://api.eotdl.com/datasets/{dataset_id}/stage/{relative_path}"
        data.append(stac_item)
gdf = gpd.GeoDataFrame(data, geometry='geometry')
gdf.to_parquet(catalog_path)
print("done")

print("uploading catalog...", end="", flush=True)
client.fput_object(
    os.environ['BUCKET'],
    f'{dataset_id}/catalog.v1.parquet',
    str(catalog_path),
)   
print("done")

print("calculating size...", end="", flush=True)
size = 0
for asset in gdf.assets:
    size += asset['asset']['size']
print("done")
print("size", size)