#  SH API rate limit: 1200 requests/minute
import geopandas as gpd
import random
import multiprocessing
from eotdl.tools import bbox_from_centroid
from dotenv import load_dotenv
import os

data_path = '/fastdata/Satellogic/data/tifs/satellogic/'


def copy_hr(output_dir=data_path + "tifs"):

    # download sentinel images to fastdata
    hr_path = ""
    print("Copied!")
    print("-------------------------")

    return hr_path


if __name__ == "__main__":
    # Get all files in the directory
    all_files = [f for f in os.listdir(data_path) if os.path.isfile(os.path.join(data_path, f))]

    # Sample 100 files (if there are at least 100 files)
    sample_size = min(100, len(all_files))
    sampled_files = random.sample(all_files, sample_size)

    # Print sampled file names
    for file in sampled_files:
        print(data_path + "/" + file)
