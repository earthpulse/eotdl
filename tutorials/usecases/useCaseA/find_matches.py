import geopandas as gpd
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from tqdm import tqdm
from eotdl.access import search_sentinel_imagery
from datetime import timedelta
from datetime import datetime

path = '/fastdata/Satellogic/data/'

NUM_SAMPLES = 1000000
TIME_BUFFER = 6 # days
NUM_CORES = multiprocessing.cpu_count()
REQUEST_LIMIT = 1200

def search_matches(args):
	"""
    Search for Sentinel-1 and Sentinel-2 satellite image matches for a given image sample.

    Parameters:
    ----------
    args : tuple
        A tuple containing:
        - row: any identifier or metadata row (e.g., index, path)
        - date: acquisition date of the target image
        - bb: bounding box [min_x, min_y, max_x, max_y] defining the search area

    Returns:
    -------
    tuple
        A tuple of the form (row, matches), where matches is a combined list of
        Sentinel-1 and Sentinel-2 image metadata that intersect the bounding box
        and are within the defined time buffer of the given date.
    """

	row, date, bb = args

	sent1_matches = find_sentinel_matches(date, bb, collection_id="sentinel-1-grd")
	sent2_matches = find_sentinel_matches(date, bb, collection_id="sentinel-2-l2a")
	sent1_matches = sent1_matches + sent2_matches

	return (row, sent1_matches)

	
if __name__ == "__main__":
	print("Reading Satellogic Earthview items... ", end="", flush=True)
	gdf = gpd.read_parquet(path + 'satellogic-earthview-items.parquet')
	gdf = gdf.sample(NUM_SAMPLES, random_state=2025)
	gdf = gdf.reset_index(drop=True)
	print("Done")
	print(f"Searching for matches for {len(gdf)} items...", end="", flush=True)
	# args = [(ix, item) for ix, item in gdf.iterrows()]
	with ProcessPoolExecutor(max_workers=NUM_CORES) as pool:
		with tqdm(total=len(gdf)) as progress:
			futures = []
			for row, item in gdf.iterrows():
				future = pool.submit(search_matches, (row, item.date, item.geometry.bounds)) 
				future.add_done_callback(lambda p: progress.update())
				futures.append(future)
			results = []
			for future in futures:
				result = future.result()
				results.append(result)
	print("Done")
	print("Saving results...", end="", flush=True)
	sorted_results = sorted(results, key=lambda x: x[0])
	matches = [r[1] for r in sorted_results]
	gdf['matches'] = matches
	gdf.to_parquet(path + 'satellogic-earthview-items-with-matches.parquet')
	print("Done")
