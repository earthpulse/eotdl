# script to prepare the dataset (download Satellogic + S1/S2 images)
#  SH API rate limit: 1200 requests/minute
REQUEST_LIMIT = 1200

import geopandas as gpd
import json
from pathlib import Path
import requests
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
from eotdl.access import download_sentinel_imagery
from datetime import datetime
from eotdl.tools import bbox_from_centroid
import os

path = '/fastdata/Satellogic/'
dst_path = '/fastdata/Satellogic/data/'

CLOUD_COVER_THRESHOLD = 0.1 # %
WIDTH = 384
HEIGHT = 384
NUM_CORES = multiprocessing.cpu_count()

def download_images(json_path0, centroid, s2_date, s1_date):
	json_path = Path(json_path0.replace('data/', path + 'data/'))
	# satellogic json metadata
	if not json_path.exists():
		json_path.parent.mkdir(parents=True, exist_ok=True)
		url = "https://satellogic-earthview.s3.us-west-2.amazonaws.com/" + json_path0
		response = requests.get(url, stream=True)
		response.raise_for_status()
		with open(json_path, 'wb') as f:
			for chunk in response.iter_content(chunk_size=8192):
				f.write(chunk)
	with open(json_path, 'r') as f:
		metadata = json.load(f)
	# satellogic image
	url = metadata['assets']['analytic']['href']
	output_path = Path(dst_path + "tifs/satellogic") / url.split('/')[-1]
	if not output_path.exists():
		try:
			output_path.parent.mkdir(parents=True, exist_ok=True)
			response = requests.get(url, stream=True)
			response.raise_for_status()
			with open(output_path, 'wb') as f:
				for chunk in response.iter_content(chunk_size=8192):
					f.write(chunk)
		except requests.exceptions.RequestException as e:
			print(f"Error downloading Satellogic imagery: {e}")
			return None
		except IOError as e:
			print(f"Error writing Satellogic imagery to file: {e}")
			return None
	# sentinel 2
	dst_path_sentinel2 = None
	if s2_date is not None:
		name = str(json_path).split('/')[-1].replace('_metadata.json', '_S2L2A')
		dst_path_sentinel2 = dst_path + "/tifs/sentinel2/" + name + '.tif'
		custom_bbox = bbox_from_centroid(x=centroid.y, y=centroid.x, pixel_size=10, width=WIDTH, height=HEIGHT)
		try:
			download_sentinel_imagery(dst_path + "/tifs/sentinel2", s2_date, custom_bbox, "sentinel-2-l2a", name=name)
			Path(str(dst_path_sentinel2).replace('.tif', '.json')).unlink(missing_ok=True)
		except Exception as e:
			print(f"Error downloading sentinel imagery: {e}")
			return None
	# sentinel 1
	dst_path_sentinel1 = None
	if s1_date is not None:
		name = str(json_path).split('/')[-1].replace('_metadata.json', '_S1GRD')
		dst_path_sentinel1 = dst_path + "/tifs/sentinel1/" + name + '.tif'
		custom_bbox = bbox_from_centroid(x=centroid.y, y=centroid.x, pixel_size=10, width=WIDTH, height=HEIGHT)
		try:
			download_sentinel_imagery(dst_path + "/tifs/sentinel1", s1_date, custom_bbox, "sentinel-1-grd", name=name)
			Path(str(dst_path_sentinel1).replace('.tif', '.json')).unlink(missing_ok=True)
		except Exception as e:
			print(f"Error downloading sentinel imagery: {e}")
			return None
		return (dst_path_sentinel2, dst_path_sentinel1, output_path)

def download_matches(args):
	s2_matches, s1_matches, date, json_path, centroid = args
	s2_date, s1_date = None, None
	if len(s2_matches) > 0:
		# filter by cloud cover
		s2_matches_filtered = [r for r in s2_matches if r['properties']['eo:cloud_cover'] <= CLOUD_COVER_THRESHOLD]
		if len(s2_matches_filtered) > 0:
			# Find closest match by date
			closest_match = min(s2_matches_filtered, key=lambda x: abs(datetime.fromisoformat(x['properties']['datetime'].replace('Z','')) - date))
			s2_date = closest_match['properties']['datetime']
	if len(s1_matches) > 0:
		# Find closest match by date
		closest_match = min(s1_matches, key=lambda x: abs(datetime.fromisoformat(x['properties']['datetime'].replace('Z','')) - date))
		s1_date = closest_match['properties']['datetime']
	return download_images(json_path, centroid, s2_date, s1_date)

if __name__ == "__main__":
	print("Reading Satellogic with matches items... ", end="", flush=True)
	gdf = gpd.read_parquet(path + 'satellogic-earthview-items-with-matches.parquet')
	print("Done")
	zones = sorted(gdf['zone'].unique())
	for z, zone in enumerate(zones):
		zone_gdf = gdf[gdf['zone'] == zone]
		print("Zone:", zone, f"({z+1}/{len(zones)})", f"({len(zone_gdf)} samples)")
		args = [(item.s2_matches, item.s1_matches, item.date, item.json_path, item.geometry.centroid) for _, item in zone_gdf.iterrows()]
		with ProcessPoolExecutor(max_workers=NUM_CORES) as pool:
			with tqdm(total=len(args)) as progress:
				futures = []
				for arg in args:
					future = pool.submit(download_matches, arg) 
					future.add_done_callback(lambda p: progress.update())
					futures.append(future)
				results = []
				for future in futures:
					result = future.result()
					results.append(result)
		print("Downloaded", sum(1 for r in results if r is not None), "matches")