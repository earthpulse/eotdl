import geopandas as gpd
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from tqdm import tqdm
from eotdl.access import search_sentinel_imagery
from datetime import timedelta

path = '/fastdata/Satellogic/data/'

NUM_SAMPLES = 100000
TIME_BUFFER = 6 # days
NUM_CORES = multiprocessing.cpu_count()
REQUEST_LIMIT = 1200

def search_matches(args):
	row, date, bb = args
	dates = [(date - timedelta(days=TIME_BUFFER/2)).strftime('%Y-%m-%d'), (date + timedelta(days=TIME_BUFFER/2)).strftime('%Y-%m-%d')]
	results = list(search_sentinel_imagery(dates, bb, 'sentinel-2-l2a'))
	return (row, results)
	
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