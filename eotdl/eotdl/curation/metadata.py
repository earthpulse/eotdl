"""
Module for EO-TDL metadata
"""

from typing import Optional

from os import remove
from glob import glob
from os.path import join


def remove_raster_metadata(folder: str, metadata_file: Optional[str] = 'metadata.json') -> None:
    """
    Remove metadata.json file from a folder

    :param folder: folder path
    :param metadata_file: metadata file name
    """
    # Search for all the metadata files in the folder
    metadata_files = glob(join(folder, "**", metadata_file), recursive=True)
    # Remove all the metadata files
    for metadata_file in metadata_files:
        remove(metadata_file)
