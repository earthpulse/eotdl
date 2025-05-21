# script to prepare the dataset (download Satellogic + S1/S2 images)
#  SH API rate limit: 1200 requests/minute
REQUEST_LIMIT = 1200

path = '/fastdata/Satellogic/data/'
dst_path = '/fastdata/Satellogic/data/'

SAMPLES_PER_ZONE= 10000 # 69 zones
TIME_BUFFER = 6 # days
CLOUD_COVER_THRESHOLD = 0.0 # %
WIDTH = 38
HEIGHT = 38

import geopandas as gpd
import json
from pathlib import Path
import requests
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
from eotdl.access import search_sentinel_imagery, download_sentinel_imagery
from datetime import datetime, timedelta
from eotdl.tools import bbox_from_centroid

def download_images(json_path, centroid, date):
	# satellogic
	with open(json_path, 'r') as f:
		metadata = json.load(f)
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
	# sentinel
	name = json_path.split('/')[-1].replace('_metadata.json', '_S2L2A')
	dst_path_sentinel = dst_path + "/tifs/sentinel2/" + name + '.tif'
	custom_bbox = bbox_from_centroid(x=centroid.y, y=centroid.x, pixel_size=10, width=WIDTH, height=HEIGHT)
	try:
		download_sentinel_imagery(dst_path + "/tifs/sentinel2", date, custom_bbox, "sentinel-2-l2a", name=name)
		Path(str(dst_path_sentinel).replace('.tif', '.json')).unlink(missing_ok=True)
	except Exception as e:
		print(f"Error downloading sentinel imagery: {e}")
		return None
	return (dst_path_sentinel, output_path)





def search_matches(args):
	date, bb, json_path, centroid = args
	bb = [bb[0], bb[1], bb[2], bb[3]]

	sent1_matches =

	if len(results) > 0:
		# filter by cloud cover
		results_filtered = [r for r in results if r['properties']['eo:cloud_cover'] <= CLOUD_COVER_THRESHOLD]
		if len(results_filtered) > 0:
			# Find closest match by date
			closest_match = min(results_filtered, key=lambda x: abs(datetime.fromisoformat(x['properties']['datetime'].replace('Z','')) - date))
			return download_images(json_path, centroid, closest_match['properties']['datetime'])
		return None
	return None

# def rate_limited_request(func, *args, **kwargs):
# 	with request_lock:
# 		current_time = time.time()
# 		# Remove requests older than 1 minute
# 		while request_times and request_times[0] < current_time - 60:
# 			request_times.pop(0)
# 		# Wait if we've hit the limit
# 		if len(request_times) >= REQUEST_LIMIT:
# 			sleep_time = request_times[0] - (current_time - 60)
# 			if sleep_time > 0:
# 				time.sleep(sleep_time)
# 		# Make the request
# 		result = func(*args, **kwargs)
# 		request_times.append(time.time())
# 		return result
	

if __name__ == "__main__":
	print("Reading Satellogic Earthview items... ", end="", flush=True)
	gdf = gpd.read_parquet(path + 'satellogic-earthview-items.parquet')
	print("Done")

	zones = sorted(gdf['zone'].unique())

	num_cores = 1 #multiprocessing.cpu_count()
	for z, zone in enumerate(zones):
		zone_gdf = gdf[gdf['zone'] == zone]
		n_samples = min(SAMPLES_PER_ZONE, len(zone_gdf))  
		print("Zone:", zone, f"({z+1}/{len(zones)})", f"({n_samples} samples)")
		sample = zone_gdf.sample(n_samples, random_state=2025)
		args = [(item.date, item.geometry.bounds, item.json_path, item.geometry.centroid) for _, item in sample.iterrows()]
		with ProcessPoolExecutor(max_workers=num_cores) as pool:
			with tqdm(total=len(args)) as progress:
				futures = []
				for arg in args:
					future = pool.submit(search_matches, arg) 
					future.add_done_callback(lambda p: progress.update())
					futures.append(future)
				results = []
				for future in futures:
					result = future.result()
					results.append(result)
		print("Found", sum(1 for r in results if r is not None), "matches")
		# break