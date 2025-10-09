from datetime import datetime, timedelta
import multiprocessing
from tqdm import tqdm
import os
import numpy as np

from ..access import search_sentinel_imagery
from ..tools import bbox_from_centroid
from .utils import _find_matches

def find_sentinel_matches_by_centroid(centroid, date, time_buffer, width, height, collection_id="sentinel-2-l2a"):
    dates = [(date - timedelta(days=time_buffer/2)).strftime('%Y-%m-%d'),
             (date + timedelta(days=time_buffer/2)).strftime('%Y-%m-%d')]
    custom_bbox = bbox_from_centroid(x=centroid.y, y=centroid.x, pixel_size=10, width=width, height=height)
    sentinel_matches = list(search_sentinel_imagery(dates, custom_bbox, collection_id))
    return sentinel_matches

def find_sentinel_matches_by_bb(bb, date, time_buffer, collection_id="sentinel-2-l2a"):
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d')
    dates = [(date - timedelta(days=time_buffer/2)).strftime('%Y-%m-%d'),
             (date + timedelta(days=time_buffer/2)).strftime('%Y-%m-%d')]
    sentinel_matches = list(search_sentinel_imagery(dates, bb, collection_id))
    return sentinel_matches

def find_matches(
    gdf, 
    time_buffer, 
    width, 
    height, 
    collection_id,
    num_cores=multiprocessing.cpu_count()
):
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=num_cores) as pool:
        args = [(ix, row.geometry.centroid, row.date, time_buffer, width, height, collection_id) for ix, row in gdf.iterrows()]
        with tqdm(total=len(args)) as progress:
            futures = []
            for arg in args:
                future = pool.submit(_find_matches, arg) # enviamos la tupla de argumentos
                future.add_done_callback(lambda p: progress.update())
                futures.append(future)
            results = []
            for future in futures:
                result = future.result()
                results.append(result)
    return results

def find_matches_chunked(
    path, 
    input_table_name,
    output_table_name,
    chunk_size, 
    num_chunks, # set to -1 to process the entire table
    seed = 2025, 
    shuffle = True,
    collections = {
        "sentinel-2-l2a": {
            'column': 's2_matches',
            'time_buffer': 30,
            'width': 384,
            'height': 384
        },
        "sentinel-1-grd": {
            'column': 's1_matches',
            'time_buffer': 6,
            'width': 384,
            'height': 384
        }
    },
    num_cores=multiprocessing.cpu_count(),
    remove_chunks=True
):
    import pyarrow.parquet as pq
    import geopandas as gpd
    from shapely import wkb
    import pandas as pd
    import gc
    import shutil

    # shutil.rmtree(path + 'chunks', ignore_errors=True)
    os.makedirs(path + 'chunks', exist_ok=True)

    print("Reading items... ", end="", flush=True)
    table = pq.read_table(path + input_table_name)
    if shuffle:
        num_rows = table.num_rows
        np.random.seed(seed)  # Set the seed for repeatability
        shuffled_indices = np.random.permutation(num_rows)
        table = table.take(shuffled_indices)
    print("Done", flush=True)

    if num_chunks < 0:
        num_chunks = (len(table) + chunk_size - 1) // chunk_size

    for i in range(num_chunks):
        if os.path.exists(path + f'chunks/chunk-{chunk_size}-{seed}-{i+1}.parquet'):
            print(f"Chunk {i+1}/{num_chunks} already exists, skipping...")
            continue
        
        start_idx = i * chunk_size
        end_idx = min(start_idx + chunk_size, len(table))

        print(f"Processing chunk {i+1}/{num_chunks}... ")
        chunk = table.slice(start_idx, end_idx - start_idx)
        df = chunk.to_pandas()
        df['geometry'] = df['geometry'].apply(wkb.loads)
        gdf_sampled = gpd.GeoDataFrame(df, geometry='geometry')

        for collection_id, param in collections.items():
            print(f"Finding {collection_id} matches... ", end="", flush=True)
            results = find_matches(gdf_sampled, param['time_buffer'], param['width'], param['height'], collection_id, num_cores)
            matches_df = pd.DataFrame(results, columns=['index', param['column']]).set_index('index')
            gdf_sampled[param['column']] = matches_df[param['column']]
            print("Done", flush=True)

        print("Saving results... ", end="", flush=True)
        gdf_sampled.to_parquet(path + f'chunks/chunk-{chunk_size}-{seed}-{i+1}.parquet')
        print("Done", flush=True)

        del chunk, df, gdf_sampled, results, matches_df
        gc.collect()


    print("Merging chunks... ", end="", flush=True)
    # chunk_files = sorted(glob(f"{path}/chunks/chunk-{chunk_size}-{seed}-*.parquet"))
    chunk_files = [path + f'chunks/chunk-{chunk_size}-{seed}-{i+1}.parquet' for i in range(num_chunks)]
    writer = None
    try:
        for chunk_file in chunk_files:
            if not os.path.exists(chunk_file):
                continue
            table = pq.read_table(chunk_file)
            if writer is None:
                writer = pq.ParquetWriter(path + output_table_name, table.schema)
            writer.write_table(table)
    finally:
        if writer is not None:
            writer.close()
    if remove_chunks:
        shutil.rmtree(path + 'chunks', ignore_errors=True)
        shutil.rmtree(path + '.chunks', ignore_errors=True)
    print("Done", flush=True)

def download_matches():
    pass