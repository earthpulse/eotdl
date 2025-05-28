import geopandas as gpd
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
from eotdl.access import search_sentinel_imagery
from dotenv import load_dotenv
from datetime import timedelta
from eotdl.tools import bbox_from_centroid

# path = '/fastdata/Satellogic/data/'
path = "~/Desktop/EarthPulse_Local_Data/data/"

TIME_BUFFER = 6  # days
NUM_CORES = multiprocessing.cpu_count()
REQUEST_LIMIT = 1200
WIDTH = 38
HEIGHT = 38

# for sentinel hub credentials
load_dotenv(dotenv_path="./.env")


def search_matches_by_sentinel(args, collection_id):
    row, date, centroid = args
    dates = [(date - timedelta(days=TIME_BUFFER/2)).strftime('%Y-%m-%d'),
             (date + timedelta(days=TIME_BUFFER/2)).strftime('%Y-%m-%d')]

    custom_bbox = bbox_from_centroid(x=centroid.y, y=centroid.x, pixel_size=10, width=WIDTH, height=HEIGHT)

    sentinel_matches = list(search_sentinel_imagery(dates, custom_bbox, collection_id))

    return row, sentinel_matches


if __name__ == "__main__":
    print("Reading Satellogic Earthview items... ", end="", flush=True)
    gdf = gpd.read_parquet(path + 'satellogic-earthview-items.parquet')
    print("Done")

    args = [(row, item.date, item.geometry.centroid) for row, item in gdf.iterrows()]

    print("Searching for Sentinel-1 matches...", flush=True)
    with ProcessPoolExecutor(max_workers=NUM_CORES) as pool:
        with tqdm(total=len(args)) as progress:
            futures = [pool.submit(search_matches_by_sentinel, arg, "sentinel-1-grd") for arg in args]
            for f in futures:
                f.add_done_callback(lambda p: progress.update())
            s1_results = [f.result() for f in futures]

    print("Searching for Sentinel-2 matches...", flush=True)
    with ProcessPoolExecutor(max_workers=NUM_CORES) as pool:
        with tqdm(total=len(args)) as progress:
            futures = [pool.submit(search_matches_by_sentinel, arg, "sentinel-2-l2a") for arg in args]
            for f in futures:
                f.add_done_callback(lambda p: progress.update())
            s2_results = [f.result() for f in futures]

    print("Combining and saving results...", flush=True)

    # Sort and assign
    s1_results = sorted(s1_results, key=lambda x: x[0])
    s2_results = sorted(s2_results, key=lambda x: x[0])
    gdf['s1_matches'] = [r[1] for r in s1_results]
    gdf['s2_matches'] = [r[1] for r in s2_results]

    gdf.to_parquet(path + 'satellogic-earthview-items-with-matches.parquet')
    print("Done")
