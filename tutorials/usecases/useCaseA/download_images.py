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

data_path = '/fastdata/Satellogic/data/'
# data_path = os.path.expanduser("~/Desktop/EarthPulse_Local_Data/data/")
# DEFAULT_OUTPUT_DIR = os.path.expanduser("~/Desktop/EarthPulse_Local_Data/data/tifs")

# for sentinel hub credentials
load_dotenv(dotenv_path="../.env")

CLOUD_COVER_THRESHOLD = 0.0  # %
WIDTH = 38
HEIGHT = 38
NUM_CORES = multiprocessing.cpu_count()
NUM_SAMPLES = 10


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

    print(f"Saving HR image to: {output_path}")

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


def download_sentinel_closest_match(closest_match, json_path, custom_bbox, collection_id, output_dir):
    sentinel = collection_data.get(collection_id)
    if not sentinel:
        print(f"Invalid collection_id: {collection_id}")
        return None

    name = json_path.split("/")[-1].replace("_metadata.json", sentinel["suffix"])
    sentinel_dst_path = f"{output_dir}/{sentinel['dir']}/{name}.tif"

    # download sentinel image only if it isn't already dwownloaded into fastdata
    if not Path(sentinel_dst_path).exists():
        try:
            download_sentinel_imagery(
                output=f"{output_dir}/{sentinel['dir']}",
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


def download_triplet_images(args, output_dir=DEFAULT_OUTPUT_DIR):
    s1_matches, s2_matches, date, json_path, centroid = args

    custom_bbox = bbox_from_centroid(x=centroid.y, y=centroid.x, pixel_size=10, width=WIDTH, height=HEIGHT)

    ### FILTERING IMAGES SECTION ###

    # filter sentinel matches by cloud cover BEFORE download (s1 doesn't have cloud cover)
    s2_matches = filter_clouds(s2_matches) or []

    # if there is not a data triplet, it does not download anything.
    if len(s1_matches) <= 0 or len(s2_matches) <= 0:
        print("❌data triplets not possible after filtering❌")
        return None, None, None

    print("s1_matches:", [match["id"] for match in s1_matches])
    print("s2_matches:", [match["id"] for match in s2_matches])

    # filter by closest date to hr image
    s1_closest_match = closest_date(s1_matches, date)
    s2_closest_match = closest_date(s2_matches, date)

    # should never be true
    if not s1_closest_match or not s2_closest_match:
        print(f"⚠️ No S1 or S2 match for: {json_path}")

    json_path = json_path.replace('data/', data_path)

    ### DOWNLOAD IMAGES ###

    # satellogic (hr) download. only downloads if path doesn't already exist.
    dst_path_sat = download_sat_image(json_path=json_path, output_path=f"{output_dir}/satellogic")

    print("Downloading S1 and S2 images...")
    # download sentinel images to fastdata
    s1_closest_match_path = download_sentinel_closest_match(closest_match=s1_closest_match,
                                                            json_path=json_path,
                                                            custom_bbox=custom_bbox,
                                                            collection_id="sentinel-1-grd",
                                                            output_dir=output_dir)

    s2_closest_match_path = download_sentinel_closest_match(closest_match=s2_closest_match,
                                                            json_path=json_path,
                                                            custom_bbox=custom_bbox,
                                                            collection_id="sentinel-2-l2a",
                                                            output_dir=output_dir)
    print("Downloaded!")
    print("-------------------------")

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


if __name__ == "__main__":
    print("Reading Satellogic Earthview items... ", end="", flush=True)
    gdf = gpd.read_parquet(data_path + 'satellogic-earthview-items-with-matches.parquet')
    print("Done\n")

    print(f"Collecting {NUM_SAMPLES} samples...", end="", flush=True)
    gdf = gdf.sample(NUM_SAMPLES).reset_index(drop=True)
    print("Done\n")

    zones = sorted(gdf['zone'].unique())
    for z, zone in enumerate(zones):
        zone_gdf = gdf[gdf['zone'] == zone]
        print("Zone:", zone, f"({z + 1}/{len(zones)})", f"({len(zone_gdf)} samples)")

        args = [
            (item.s1_matches, item.s2_matches, item.date, item.json_path, item.geometry.centroid)
            for _, item in zone_gdf.iterrows()
        ]

        results = []

        for i, arg in enumerate(args):
            print(f"\n------- SAMPLE {i} -------")
            result = download_triplet_images(args=arg, output_dir="sample")
            results.append(result)
            print("-----------------------------")

        # Count how many images were actually downloaded
        hr_count = sum(1 for r in results if r and r[2])
        s1_count = sum(1 for r in results if r and r[0])
        s2_count = sum(1 for r in results if r and r[1])
        triplet_count = sum(1 for r in results if r and all(x is not None for x in r))

        # Print summary
        print(f"\nTotal downloaded:")
        print(f"  HR images:        {hr_count}")
        print(f"  S1 matches:       {s1_count}")
        print(f"  S2 matches:       {s2_count}")
        print(f"  Full triplets:    {triplet_count}\n")


        # with ProcessPoolExecutor(max_workers=NUM_CORES) as pool:
        #     with tqdm(total=len(args)) as progress:
        #         futures = []
        #
        #         # iterate through each sample in the zone
        #         nSample = 0
        #         for arg in args:
        #             print(f"------- SAMPLE {nSample} -------")
        #             future = pool.submit(download_images_to_fastdata, arg)
        #             future.add_done_callback(lambda p: progress.update())
        #             futures.append(future)
        #             nSample += 1
        #
        #         results = [future.result() for future in futures]
