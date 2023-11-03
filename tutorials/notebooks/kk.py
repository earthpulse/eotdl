from eotdl.datasets import download_dataset

dst_path = download_dataset("eurosat-rgb", force=True, assets=True, verbose=True)
dst_path
