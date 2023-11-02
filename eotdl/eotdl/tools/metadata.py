"""
Metadata utilities for STAC
"""

import json

from os.path import dirname, join, exists, splitext
from os import listdir, remove
from glob import glob
from typing import Optional


def get_item_metadata(raster_path: str) -> str:
    """
    Get the metadata JSON file of a given directory, associated to a raster file

    :param raster_path: path to the raster file
    """
    # Get the directory of the raster file
    raster_dir_path = dirname(raster_path)
    # Get the metadata JSON file
    # Check if there is a metadata.json file in the directory
    if "metadata.json" in listdir(raster_dir_path):
        metadata_json = join(raster_dir_path, "metadata.json")
    else:
        # If there is no metadata.json file in the directory, check if there is
        # a json file with the same name as the raster file
        base = splitext(raster_path)[0]
        metadata_json = base + ".json"
        if not exists(metadata_json):
            # If there is no metadata file in the directory, return None
            return None

    # Open the metadata file and return it
    with open(metadata_json, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    return metadata


def remove_raster_metadata(
    folder: str, metadata_file: Optional[str] = "metadata.json"
) -> None:
    """
    Remove metadata.json file from a folder

    :param folder: folder path
    :param metadata_file: metadata file name
    """
    # Search for all the metadata files in the folder
    metadata_files = glob(join(folder, "**", metadata_file), recursive=True)
    # Remove all the metadata files
    for metadata in metadata_files:
        remove(metadata)
