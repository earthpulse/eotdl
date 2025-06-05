from tqdm import tqdm
import utils
import geopandas as gpd

NUM_SAMPLES = 100000
NUM_CORES = 20
path = 'outputs/'

print("Reading Satellogic items... ", end="", flush=True)
gdf = gpd.read_parquet(path + 'satellogic-earthview-items.parquet')
print("Done")

print(f"Sampling {NUM_SAMPLES} items... ", end="", flush=True)
gdf_sampled = gdf.sample(NUM_SAMPLES, random_state=2025)
gdf_sampled = gdf_sampled.reset_index(drop=True)
print("Done")

def find_matches_parallel(gdf, time_buffer=30, width=384, height=384, collection_id="sentinel-2-l2a"):
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=NUM_CORES) as pool:
        args = [(ix, row.geometry.centroid, row.date, time_buffer, width, height, collection_id) for ix, row in gdf.iterrows()]
        with tqdm(total=len(args)) as progress:
            futures = []
            for arg in args:
                future = pool.submit(utils._find_matches, arg) # enviamos la tupla de argumentos
                future.add_done_callback(lambda p: progress.update())
                futures.append(future)
            results = []
            for future in futures:
                result = future.result()
                results.append(result)
    return results

# Sentinel 2
print("Finding Sentinel 2 matches... ", end="", flush=True)
results = find_matches_parallel(gdf_sampled)
sorted_results = sorted(results, key=lambda x: x[0])
s2_matches = [r[1] for r in sorted_results]
gdf_sampled['s2_matches'] = s2_matches
print("Done")

# Sentinel 1
print("Finding Sentinel 1 matches... ", end="", flush=True)
results = find_matches_parallel(gdf_sampled, collection_id="sentinel-1-grd")
sorted_results = sorted(results, key=lambda x: x[0])
s1_matches = [r[1] for r in sorted_results]
gdf_sampled['s1_matches'] = s1_matches
print("Done")

print("Saving results... ", end="", flush=True)
gdf_sampled.to_parquet(path + 'satellogic-earthview-items-with-matches.parquet')
print("Done")
