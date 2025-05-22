# script to prepare the dataset (download Satellogic + S1/S2 images)
#  SH API rate limit: 1200 requests/minute
from typing import Tuple, Any, List

REQUEST_LIMIT = 1200

path = '/fastdata/Satellogic/data/'
dst_path = '/fastdata/Satellogic/data/'

SAMPLES_PER_ZONE = 10000  # 69 zones
TIME_BUFFER = 6  # days
CLOUD_COVER_THRESHOLD = 0.0  # %
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
from download_images import download_sat_image, get_closest_match, download_images


def find_sentinel_matches(date, bb, json_path, centroid, name, collection_id: str):
    dates = [(date - timedelta(days=TIME_BUFFER / 2)).strftime('%Y-%m-%d'),
             (date + timedelta(days=TIME_BUFFER / 2)).strftime('%Y-%m-%d')]
    results = list(search_sentinel_imagery(dates, bb, collection_id))  # why does search_sentinel_imagery return None?

    closest_match = get_closest_match(results, date)
    if not closest_match:
        return None

    sat_path = download_sat_image(closest_match, json_path)
    # sent_path = download_sentinel_image(closest_match=closest_match,
    #
    #                                     sat_path=sat_path,
    #                                     )

    return download_images(json_path, centroid, closest_match["properties"]["datetime"])


# outdated (?)
def search_matches(args):
    date, bb, json_path, centroid = args
    dates = [(date - timedelta(days=TIME_BUFFER / 2)).strftime('%Y-%m-%d'),
             (date + timedelta(days=TIME_BUFFER / 2)).strftime('%Y-%m-%d')]
    bb = [bb[0], bb[1], bb[2], bb[3]]
    results = list(search_sentinel_imagery(dates, bb, 'sentinel-2-l2a'))

    closest_match = get_closest_match(results, date)
    if closest_match:
        return None

    return download_images(json_path, centroid, closest_match["properties"]["datetime"])


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

    num_cores = 1  #multiprocessing.cpu_count()
    for z, zone in enumerate(zones):
        zone_gdf = gdf[gdf['zone'] == zone]
        n_samples = min(SAMPLES_PER_ZONE, len(zone_gdf))
        print("Zone:", zone, f"({z + 1}/{len(zones)})", f"({n_samples} samples)")
        sample = zone_gdf.sample(n_samples, random_state=2025)
        args = [(item.date, item.geometry.bounds, item.json_path, item.geometry.centroid) for _, item in
                sample.iterrows()]

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
