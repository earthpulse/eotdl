from tqdm import tqdm
import utils
import geopandas as gpd
import pyarrow.parquet as pq
import pyarrow as pa
import os
from glob import glob
from shapely import wkb
import shutil
import numpy as np

CHUNK_SIZE = 10_000
NUM_CHUNKS = 100 # set to -1 to process the entire table
NUM_CORES = 20
SHUFFLE = True # so we have samples from all regions even if we don't process all the rows
SEED = 2025

path = 'outputs/'

def find_matches_parallel(gdf, time_buffer=30, width=384, height=384, collection_id="sentinel-2-l2a"):
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=NUM_CORES) as pool:
        args = [(ix, row.geometry.centroid, row.date, time_buffer, width, height, collection_id) for ix, row in gdf.iterrows()]
        with tqdm(total=len(args), desc=f"{collection_id}") as progress:
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

# shutil.rmtree(path + 'chunks', ignore_errors=True)
os.makedirs(path + 'chunks', exist_ok=True)

print("Reading Satellogic items... ", end="", flush=True)
table = pq.read_table(path + 'satellogic-earthview-items.parquet')
if SHUFFLE:
    num_rows = table.num_rows
    np.random.seed(SEED)  # Set the seed for repeatability
    shuffled_indices = np.random.permutation(num_rows)
    table = table.take(shuffled_indices)
print("Done")

if NUM_CHUNKS < 0:
    NUM_CHUNKS = len(table) // CHUNK_SIZE + 1

for i in range(NUM_CHUNKS):
    if os.path.exists(path + f'chunks/chunk-{CHUNK_SIZE}-{SEED}-{i+1}.parquet'):
        print(f"Chunk {i+1}/{NUM_CHUNKS} already exists, skipping...")
        continue
    
    start_idx = i * CHUNK_SIZE
    end_idx = start_idx + CHUNK_SIZE if i < NUM_CHUNKS - 1 else len(table)

    print(f"Processing chunk {i+1}/{NUM_CHUNKS}... ")
    chunk = table.slice(start_idx, end_idx - start_idx)
    df = chunk.to_pandas()
    df['geometry'] = df['geometry'].apply(wkb.loads)
    gdf_sampled = gpd.GeoDataFrame(df, geometry='geometry')

    # Sentinel 2
    results = find_matches_parallel(gdf_sampled)
    sorted_results = sorted(results, key=lambda x: x[0])
    s2_matches = [r[1] for r in sorted_results]
    gdf_sampled['s2_matches'] = s2_matches

    # Sentinel 1
    results = find_matches_parallel(gdf_sampled, collection_id="sentinel-1-grd")
    sorted_results = sorted(results, key=lambda x: x[0])
    s1_matches = [r[1] for r in sorted_results]
    gdf_sampled['s1_matches'] = s1_matches

    print("Saving results... ", end="", flush=True)
    gdf_sampled.to_parquet(path + f'chunks/chunk-{CHUNK_SIZE}-{SEED}-{i+1}.parquet')
    print("Done")


print("Merging chunks... ", end="", flush=True)
chunk_files = sorted(glob(f"{path}/chunks/chunk-*.parquet"))
tables = [pq.read_table(f) for f in chunk_files]
merged_table = pa.concat_tables(tables)
pq.write_table(merged_table, path + 'satellogic-earthview-items-merged.parquet')
# shutil.rmtree(path + 'chunks', ignore_errors=True)
print("Done")
