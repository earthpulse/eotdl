"""
Module for formatter classes
"""

import json
import rasterio 

from typing import Optional
from os.path import join, dirname
from os import makedirs
from glob import glob
from shutil import rmtree, copyfile
from .base import FolderFormatter


class SHFolderFormatter(FolderFormatter):
    """
    Class for formatting the directories of Sentinel images downloaded from Sentinel Hub Services
    """

    def __init__(self, root_folder):
        super().__init__()
        self.root = root_folder

    @classmethod
    def structured_format_folders(self) -> None:
        """
        Format the folder structure of the downloaded data from Sentinel Hub to a 
        digestible format, suitable for STAC metadata generation.

        This formatted format is a structured format, where every image is located in
        a single folder, with its metadata.
        """
        images = glob(join(self.root, '**/*.tiff'), recursive=True)
        
        for image in images:
            # Folder with the request and response, with the if of the request
            image_dir = dirname(image)
            # Destination folder, with format <id>_<date>
            dest_dir = dirname(image_dir)
            # Get the request.json file with the request parameters
            request_file = join(image_dir, 'request.json')
            request_json = json.load(open(request_file))
            # Generate a metadata.json file of the raster in the destination folder
            # It will extract some needed parameters, which will be used later 
            # for the STAC generation
            # It also returns the data type of the response
            data_type = self.generate_raster_metadata(request_json, image, dest_dir)       
            # Copy the response tiff to the destination folder
            copyfile(image, join(dest_dir, f'{data_type}.tiff'))
            # Remove the request and response folder
            rmtree(image_dir)

    def unestructured_format_folders(self, output_folder: Optional[str] = None) -> None:
        """
         Format the folder structure of the downloaded data from Sentinel Hub to a 
        digestible format, suitable for STAC metadata generation and labeling with SCANEO.
        
        This formatted format is a unestructured format, where all the images are located
        into the same folder, with them metadata files with the same name as the image.
        """
        images = glob(join(self.root, '**/*.tiff'), recursive=True)

        if not output_folder:
            output_folder = self.root
        makedirs(output_folder, exist_ok=True)

        n = 0
        for image in images:
            # Folder with the request and response, with the id of the request
            image_dir = dirname(image)
            # Parent image folder, with format <id>_<date>
            parent_dir = dirname(image_dir)
            parent_dir_name = parent_dir.split('/')[-1]
            parent_dir_name_split = parent_dir_name.split('_')
            id = parent_dir_name_split[0]   # ID of the given location
            # Get the request.json file with the request parameters
            request_file = join(image_dir, 'request.json')
            request_json = json.load(open(request_file))
            # Generate a metadata.json file of the raster in the destination folder
            # It will extract some needed parameters, which will be used later 
            # for the STAC generation
            # As file name, we give the same name as de image, which is <id>_<n>
            n += 1
            filename = f'{id}_{n}'
            self.generate_raster_metadata(request_json, image, output_folder, filename)    
            # Copy the response tiff to the destination folder
            copyfile(image, join(output_folder, f'{filename}.tif'))
            # Remove the request and response folder
            rmtree(parent_dir)

    def generate_raster_metadata(self,
                                 request_json: dict,
                                 raster_path: str,
                                 output_folder: str,
                                 output_name: Optional[str] = 'metadata'
                                 ) -> None:
        """
        Generate metadata.json file for a raster file

        :param raster_path: path to the raster file
        :param output_folder: output folder to write the metadata.json file to
        :param date_adquired: date adquired of the raster file
        :param output_name: name of the metadata file
        """
        # Get the date adquired from the request json
        with rasterio.open(raster_path) as ds:
            bounds = ds.bounds
            dst_crs = "EPSG:4326"
            left, bottom, right, top = rasterio.warp.transform_bounds(
                ds.crs, dst_crs, *bounds
            )
            bbox = [left, bottom, right, top]

        payload_data = request_json['request']['payload']['input']['data'][0]
        # Get the data type from the request json
        data_type = payload_data['type']
        # Get the acquision date from the request json
        if 'timeRange' in payload_data['dataFilter']:
            data_acquisition_date = payload_data['dataFilter']['timeRange']['from']
        else:   # DEM data does not have a timeRange
            data_acquisition_date = None

        # Generate the metadata.json file
        metadata_path = join(output_folder, f"{output_name}.json")
        metadata = {
            "acquisition-date": data_acquisition_date,
            "bounding-box": bbox,
            "type": data_type,
        }

        with open(metadata_path, "w") as f:
            json.dump(metadata, f)

        return data_type
