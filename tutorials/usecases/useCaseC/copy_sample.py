#  SH API rate limit: 1200 requests/minute
import random
import os
import shutil

data_path = '/fastdata/Satellogic/data/tifs/satellogic/'

NUM_SAMPLES = 100

if __name__ == "__main__":
    # Get all files in the directory
    all_files = [f for f in os.listdir(data_path) if os.path.isfile(os.path.join(data_path, f))]

    # Sample 100 files (if there are at least 100 files)
    sample_size = min(NUM_SAMPLES, len(all_files))
    sampled_files = random.sample(all_files, sample_size)

    # Print sampled file names
    for file in sampled_files:
        path = data_path + file
        print(f"copying {file}...")
        shutil.copy2(path, "./samples/")

