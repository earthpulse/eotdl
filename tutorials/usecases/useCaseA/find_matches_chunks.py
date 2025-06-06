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
import pandas as pd
import gc

CHUNK_SIZE = 100
NUM_CHUNKS = 3 # set to -1 to process the entire table
NUM_CORES = 20
SHUFFLE = True # so we have samples from all regions even if we don't process all the rows
SEED = 2025

path = 'outputs/'

def find_matches_parallel(gdf, time_buffer=20, width=384, height=384, collection_id="sentinel-2-l2a"):
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=NUM_CORES) as pool:
        args = [(ix, row.geometry.centroid, row.date, time_buffer, width, height, collection_id) for ix, row in gdf.iterrows()]
        results = list(tqdm(pool.map(utils._find_matches, args), total=len(args), desc=f"{collection_id}"))
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
    NUM_CHUNKS = (len(table) + CHUNK_SIZE - 1) // CHUNK_SIZE

for i in range(NUM_CHUNKS):
    if os.path.exists(path + f'chunks/chunk-{CHUNK_SIZE}-{SEED}-{i+1}.parquet'):
        print(f"Chunk {i+1}/{NUM_CHUNKS} already exists, skipping...")
        continue
    
    start_idx = i * CHUNK_SIZE
    end_idx = min(start_idx + CHUNK_SIZE, len(table))

    print(f"Processing chunk {i+1}/{NUM_CHUNKS}... ")
    chunk = table.slice(start_idx, end_idx - start_idx)
    df = chunk.to_pandas()
    df['geometry'] = df['geometry'].apply(wkb.loads)
    gdf_sampled = gpd.GeoDataFrame(df, geometry='geometry')

    # Sentinel 2
    results = find_matches_parallel(gdf_sampled)
    s2_matches_df = pd.DataFrame(results, columns=['index', 's2_matches']).set_index('index')
    gdf_sampled['s2_matches'] = s2_matches_df['s2_matches']

    # Sentinel 1
    results = find_matches_parallel(gdf_sampled, collection_id="sentinel-1-grd")
    s1_matches_df = pd.DataFrame(results, columns=['index', 's1_matches']).set_index('index')
    gdf_sampled['s1_matches'] = s1_matches_df['s1_matches']

    print("Saving results... ", end="", flush=True)
    gdf_sampled.to_parquet(path + f'chunks/chunk-{CHUNK_SIZE}-{SEED}-{i+1}.parquet')
    print("Done")

    del chunk, df, gdf_sampled, results, s2_matches_df, s1_matches_df
    gc.collect()


print("Merging chunks... ", end="", flush=True)
# chunk_files = sorted(glob(f"{path}/chunks/chunk-{CHUNK_SIZE}-{SEED}-*.parquet"))
chunk_files = [path + f'chunks/chunk-{CHUNK_SIZE}-{SEED}-{i+1}.parquet' for i in range(NUM_CHUNKS)]
writer = None
try:
    for chunk_file in chunk_files:
        if not os.path.exists(chunk_file):
            continue
        table = pq.read_table(chunk_file)
        if writer is None:
            writer = pq.ParquetWriter(path + 'satellogic-earthview-items-with-matches.parquet', table.schema)
        writer.write_table(table)
finally:
    if writer is not None:
        writer.close()
# shutil.rmtree(path + 'chunks', ignore_errors=True)
print("Done")
