# script to prepare the dataset (download Satellogic + S1/S2 images)
#  SH API rate limit: 1200 requests/minute
import os.path

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
from dotenv import load_dotenv

path = '/fastdata/Satellogic/data/'
dst_path = '/fastdata/Satellogic/data/'
# path = os.path.expanduser("~/Desktop/EarthPulse_Local_Data/data/")
# dst_path = os.path.expanduser("~/Desktop/EarthPulse_Local_Data/data/")

# for sentinel hub credentials
load_dotenv(dotenv_path="./.env")

CLOUD_COVER_THRESHOLD = 0.0  # %
WIDTH = 38
HEIGHT = 38
NUM_CORES = multiprocessing.cpu_count()
REQUEST_LIMIT = 1200

# dir is the location in fastdata/tifs. Suffix is the tail of the filename of the sentinel tif file.
collection_data = {
    "sentinel-1-grd": {"dir": "sentinel1", "suffix": "_S1GRD"},
    "sentinel-2-l2a": {"dir": "sentinel2", "suffix": "_S2L2A"},
}


def filter_clouds(matches):
    matches_filtered = [r for r in matches if r['properties']['eo:cloud_cover'] <= CLOUD_COVER_THRESHOLD]
    if len(matches_filtered) <= 0:
        return None
    return matches_filtered


def closest_date(matches, date):
    # if no results
    if len(matches) <= 0:
        return None

    # closest image by date
    closest_match = min(matches,
                        key=lambda x: abs(datetime.fromisoformat(x['properties']['datetime'].replace('Z', '')) - date))
    return closest_match


def download_sat_image(json_path, output_path):
    # get path to metadata file
    with open(json_path, 'r') as f:
        metadata = json.load(f)

    # get download link from metadata
    url = metadata['assets']['analytic']['href']

    output_path = Path(output_path) / url.split('/')[-1]

    # make path where the sat (hr) image will be saved. download, and then write in chunks to that location.
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

    return output_path


def download_sentinel_closest_match(matches, satellogic_date, json_path, custom_bbox, collection_id):

    sentinel = collection_data.get(collection_id)
    if not sentinel:
        print(f"Invalid collection_id: {collection_id}")
        return None

    name = json_path.split("/")[-1].replace("_metadata.json", sentinel["suffix"])
    sentinel_dst_path = f"{dst_path}/tifs/{sentinel['dir']}/{name}.tif"
    closest_match = closest_date(matches, satellogic_date)

    if closest_match is None:
        print(f"No valid {collection_id} match for {json_path}")
        return None

    # download sentinel image only if it isn't already dwownloaded into fastdata
    if not Path(sentinel_dst_path).exists():
        try:
            download_sentinel_imagery(
                output=f"{dst_path}/tifs/{sentinel['dir']}",
                time_interval=closest_match["properties"]["datetime"],
                bounding_box=custom_bbox,
                collection_id=collection_id,
                name=name
            )
            Path(sentinel_dst_path.replace('.tif', '.json')).unlink(missing_ok=True)
        except Exception as e:
            print(f"❌ Error downloading {collection_id}: {e}")
            return None

    return sentinel_dst_path


def download_images_to_fastdata(args):
    s1_matches, s2_matches, date, json_path, centroid = args

    json_path = json_path.replace('data/', path)
    print(json_path)

    # satellogic (hr) download. only downloads if path doesn't already exist.
    dst_path_sat = download_sat_image(json_path=json_path, output_path=dst_path + "tifs/satellogic")

    custom_bbox = bbox_from_centroid(x=centroid.y, y=centroid.x, pixel_size=10, width=WIDTH, height=HEIGHT)

    # filter sentinel matches by cloud cover BEFORE download
    # s1_matches = filter_clouds(s1_matches) or [] <- S1 doesn't have a cloud cover property
    s2_matches = filter_clouds(s2_matches) or []

    s1_closest_match_path = download_sentinel_closest_match(s1_matches, date, json_path, custom_bbox, collection_id="sentinel-1-grd")
    s2_closest_match_path = download_sentinel_closest_match(s2_matches, date, json_path, custom_bbox, collection_id="sentinel-2-l2a")

    # # download all sentinel matches. set their file name to their id.
    #
    # s1_match_paths = []
    # # download all s1 matches.
    # for match in s1_matches:
    #     # create name for download path
    #     name = match['id']
    #     s1_path = dst_path + "/tifs/sentinel1/" + name + '.tif'
    #
    #     try:
    #         download_sentinel_imagery(dst_path + "/tifs/sentinel1", match["properties"]["datetime"], custom_bbox,
    #                                   "sentinel-1-grd", name=name)
    #         Path(str(s1_path).replace('.tif', '.json')).unlink(missing_ok=True)  # ????
    #         s1_match_paths.append(s1_path)
    #     except Exception as e:
    #         print(f"Error downloading sentinel imagery: {e}")
    #
    # s2_match_paths = []
    # # download all s2 matches.
    # for match in s2_matches:
    #     # create name for download path
    #     name = match['id']
    #     s2_path = dst_path + "/tifs/sentinel2/" + name + '.tif'
    #
    #     try:
    #         download_sentinel_imagery(dst_path + "/tifs/sentinel2", match["properties"]["datetime"], custom_bbox,
    #                                   "sentinel-2-l2a", name=name)
    #         Path(str(s2_path).replace('.tif', '.json')).unlink(missing_ok=True)  # ????
    #         s2_match_paths.append(s2_path)
    #     except Exception as e:
    #         print(f"Error downloading sentinel imagery: {e}")

    return s1_closest_match_path, s2_closest_match_path, dst_path_sat


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
    gdf = gpd.read_parquet(path + 'satellogic-earthview-items-with-matches.parquet')
    print("Done")

    zones = sorted(gdf['zone'].unique())

    for z, zone in enumerate(zones):
        zone_gdf = gdf[gdf['zone'] == zone]
        print("Zone:", zone, f"({z + 1}/{len(zones)})", f"({len(zone_gdf)} samples)")

        args = [
            (item.s1_matches, item.s2_matches, item.date, item.json_path, item.geometry.centroid)
            for _, item in zone_gdf.iterrows()
        ]

        with ProcessPoolExecutor(max_workers=NUM_CORES) as pool:
            with tqdm(total=len(args)) as progress:
                futures = []
                for arg in args:
                    future = pool.submit(download_images_to_fastdata, arg)
                    future.add_done_callback(lambda p: progress.update())
                    futures.append(future)

                results = [future.result() for future in futures]

        hr_count = sum(1 for r in results if r and r[2])
        s1_count = sum(1 for r in results if r and r[0])
        s2_count = sum(1 for r in results if r and r[1])
        triplet_count = sum(1 for r in results if r and all(r))

        print(f"Total downloaded:")
        print(f"  HR images:        {hr_count}")
        print(f"  S1 matches:       {s1_count}")
        print(f"  S2 matches:       {s2_count}")
        print(f"  Full triplets:    {triplet_count}")
