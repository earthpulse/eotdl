"""
Module for generating STAC metadata 
"""

import pandas as pd
import json
from typing import Optional
import pystac
from pystac.extensions.sar import SarExtension
from pystac.extensions.sar import FrequencyBand, Polarization
from pystac.extensions.eo import Band, EOExtension
from random import sample

from os import listdir
from os.path import join, isdir, basename, exists, dirname

import rasterio
from rasterio.warp import transform_bounds

from datetime import datetime
from shapely.geometry import Polygon, mapping
from glob import glob

from .utils import format_time_acquired, count_ocurrences
from .extensions import type_stac_extensions_dict


class STACGenerator:
        
    def __init__(self) -> None:
        self._image_format = None
        self._extensions_dict: dict = type_stac_extensions_dict
        self._stac_dataframe = None

    def generate_stac_metadata(self,
                               stac_dataframe: pd.DataFrame,
                               id: str,
                               description: str,
                               output: str = 'stac',                               
                               extensions: dict=None,
                               image_format: str='tiff',
                               catalog_type: pystac.CatalogType=pystac.CatalogType.SELF_CONTAINED, 
                               **kwargs) -> None:
        """
        Generate STAC metadata for a given directory containing the assets to generate metadata

        :param stac_dataframe: dataframe with the STAC metadata of a given directory containing the assets to generate metadata
        :param id: id of the catalog
        :param description: description of the catalog
        :param output: output folder to write the catalog to
        :param extensions: dictionary with the extensions
        :param image_format: image format of the assets
        :param kwargs: optional arguments. Possible values:
            - description: description of the catalog
            - keywords: keywords of the catalog
        """
        self._image_format = image_format
        self._stac_dataframe = stac_dataframe
        
        # Create an empty catalog
        catalog = self.create_stac_catalog(id=id, description=description)
        
        # Add the collections to the catalog
        collections = self._stac_dataframe.collection.unique()
        for collection_path in collections:
            # Generate the collection
            collection = self.generate_stac_collection(collection_path)
            # Add the collection to the catalog
            catalog.add_child(collection)
        
        # Add the catalog to the root directory
        catalog.normalize_hrefs(output)
        # catalog.validate_all()
        catalog.save(catalog_type=catalog_type)

        return catalog   # DEBUG

    def get_stac_dataframe(self, path: str, bands: dict=None, extensions: dict=None, image_format: str='tiff') -> pd.DataFrame:
        """
        Get a dataframe with the STAC metadata of a given directory containing the assets to generate metadata

        :param path: path to the root directory
        :param extensions: dictionary with the extensions
        :param image_format: image format of the assets
        """
        images = glob(str(path) + f'/**/*.{image_format}', recursive=True)
        images = sample(images, 50)   # debug
        labels, ixs = self._format_labels(images)
        bands = self._get_items_list_from_dict(labels, bands)
        exts = self._get_items_list_from_dict(labels, extensions)
        collections = self._get_images_common_prefix(images)

        df = pd.DataFrame({'image': images, 
                           'label': labels, 
                           'ix': ixs, 
                           'collection': collections, 
                           'extensions': exts, 
                           'bands': bands})
        
        return df
    
    def _get_images_common_prefix(self, images: list) -> list:
        """
        Get the common prefix of a list of images

        :param images: list of images
        """
        images_common_prefix_dict = dict()

        images_dirs = list(set([dirname(i) for i in images]))

        for image in images_dirs:
            path = image
            common = False
            while not common:
                n = count_ocurrences(path, images_dirs)
                if n > 1:
                    images_common_prefix_dict[image] = path
                    common = True
                else:
                    path = dirname(path)

        images_common_prefix_list = list()
        for i in images:
            images_common_prefix_list.append(images_common_prefix_dict[dirname(i)])

        return images_common_prefix_list
    
    
    def _format_labels(self, images):
        """
        Format the labels of the images

        :param images: list of images
        """
        labels = [x.split('/')[-1].split('_')[0].split('.')[0] for x in images]
        ixs = [labels.index(x) for x in labels]
        return labels, ixs
    
    def _get_items_list_from_dict(self, labels: list, items: dict) -> list:
        """
        """
        if not items:
            # Create list of None with the same length as the labels list
            return [None for _ in labels]
        items_list = list()
        for label in labels:
            if label in items.keys():
                items_list.append(items[label])
            else:
                items_list.append(None)

        return items_list
    
    def _get_collection_extent(self, path: str) -> pystac.Extent:
        """
        Get the extent of a collection
        
        :param path: path to the directory
        """
        # Get the spatial extent of the collection
        spatial_extent = self._get_collection_spatial_extent(path)
        # Get the temporal interval of the collection
        temporal_interval = self._get_collection_temporal_interval(path)
        # Create the Extent object
        extent = pystac.Extent(spatial=spatial_extent, temporal=temporal_interval)

        return extent
    
    def _get_collection_spatial_extent(self, path: str) -> pystac.SpatialExtent:
        """
        Get the spatial extent of a collection

        :param path: path to the directory
        """
        # Get the bounding boxes of all the rasters in the path
        bboxes = list()
        # use glob
        rasters = glob(f'{path}/**/*.{self._image_format}', recursive=True)
        for raster in rasters:
            with rasterio.open(raster) as ds:
                bounds = ds.bounds
                dst_crs = 'EPSG:4326'
                try:
                    left, bottom, right, top = rasterio.warp.transform_bounds(ds.crs, dst_crs, *bounds)
                    bbox = [left, bottom, right, top]
                except rasterio.errors.CRSError:
                    spatial_extent = pystac.SpatialExtent([[None, None, None, None]])
                    return spatial_extent
                finally:
                    bboxes.append(bbox)
        # Get the minimum and maximum values of the bounding boxes
        try:
            left = min([bbox[0] for bbox in bboxes])
            bottom = min([bbox[1] for bbox in bboxes])
            right = max([bbox[2] for bbox in bboxes])
            top = max([bbox[3] for bbox in bboxes])
            spatial_extent = pystac.SpatialExtent([[left, bottom, right, top]])
        except ValueError:
            spatial_extent = pystac.SpatialExtent([[None, None, None, None]])
        finally:
            return spatial_extent
    
    def _get_collection_temporal_interval(self, path: str) -> pystac.TemporalExtent:
        """
        Get the temporal interval of a collection

        :param path: path to the directory
        """
        # Get all the metadata.json files in the path
        metadata_json_files = glob(f'{path}/**/*.json', recursive=True)
        if not metadata_json_files:
            min_date = datetime.strptime('2000-01-01', '%Y-%m-%d')
            max_date = datetime.strptime('2023-12-31', '%Y-%m-%d')
            return pystac.TemporalExtent([min_date, max_date])   # TODO Unknown temporal interval
        
        # Get the temporal interval of every metadata.json file
        temporal_intervals = list()
        for metadata_json_file in metadata_json_files:
            with open(metadata_json_file, 'r') as f:
                metadata = json.load(f)
            temporal_intervals.append(metadata['date-adquired']) if metadata['date-adquired'] else None
        if temporal_intervals:   # TODO control in DEM data
            try:
                # Get the minimum and maximum values of the temporal intervals
                min_date = min([datetime.strptime(interval, '%Y-%m-%d') for interval in temporal_intervals])
                max_date = max([datetime.strptime(interval, '%Y-%m-%d') for interval in temporal_intervals])
            except ValueError:
                min_date = datetime.strptime('2000-01-01', '%Y-%m-%d')
                max_date = datetime.strptime('2023-12-31', '%Y-%m-%d')
            finally:
                # Create the temporal interval
                temporal_interval = pystac.TemporalExtent([min_date, max_date])

            return temporal_interval

    def create_stac_catalog(self, id: str, description: str, params: dict=None) -> pystac.Catalog:
        """
        Create a STAC catalog

        :param id: id of the catalog
        :param kwargs: optional arguments. Possible values:
            - description: description of the catalog
            - keywords: keywords of the catalog
        """
        if not params:
            return pystac.Catalog(id=id, description=description)
        else:
            return pystac.Catalog(id=id, description=description, **params)
    
    def update_stac_catalog(self, catalog: pystac.Catalog, **kwargs) -> pystac.Catalog:
        """
        """
        # Update the catalog with the given arguments
        pass

    def generate_stac_collection(self, path: str) -> pystac.Collection:
        """
        Generate a STAC collection from a directory containing the assets to generate metadata

        :param path: path to the root directory
        """
        # Get the collection extent
        extent = self._get_collection_extent(path)
        # Create the collection
        collection = pystac.Collection(id=basename(path),
                                        description='Collection',
                                        extent=extent)
        
        for image in self._stac_dataframe.image:
            # Check if the path of the image is a child of the path of the collection
            if path in image:
                # Create the item
                item = self.create_stac_item(image)
                # Add the item to the collection
                collection.add_item(item)
        
        # Return the collection
        return collection

    def create_stac_collection(self, id: str, description: str, extent: pystac.Extent, **kwargs) -> pystac.Collection:
        """
        Create a STAC collection
        """
        return pystac.Collection(id=id, description=description, extent=extent)

    def update_stac_collection(self, collection: pystac.Collection, **kwargs) -> pystac.Collection:
        """
        Update a STAC collection
        """
        pass

    def create_stac_item(self,
                        raster_path: str
                        ) -> pystac.Item:
        """
        Create a STAC item from a directory containing the raster files and the metadata.json file

        :param tiff_dir_path: path to the directory containing the raster files
        :param metadata_json: path to the metadata.json file
        :param collection: pystac.Collection object
        :param extensions: list of extensions to add to the item
        :return: pystac.Item object
        """
        # Check if there is any metadata file in the directory associated to the raster file
        metadata = self._get_item_metadata(raster_path)

        # Obtain the bounding box from the raster
        with rasterio.open(raster_path) as ds:
            bounds = ds.bounds
            dst_crs = 'EPSG:4326'
            try:
                left, bottom, right, top = rasterio.warp.transform_bounds(ds.crs, dst_crs, *bounds)
            except rasterio.errors.CRSError:
                left, bottom, right, top = None, None, None, None

        # Create bbox
        bbox = [left, bottom, right, top]

        # Create geojson feature
        # If the bounding box has no values, set the geometry to None
        if not bbox[0] or not bbox[1] or not bbox[2] or not bbox[3]:
            geom = None
        else:
            geom = mapping(Polygon([
            [left, bottom],
            [left, top],
            [right, top],
            [right, bottom]
            ]))

        # Initialize properties
        properties = dict()

        # Obtain the date acquired
        if metadata and metadata["date-adquired"]:
            time_acquired = format_time_acquired(metadata["date-adquired"])
        else:
            # Set unknown date
            time_acquired = datetime.strptime('2000-01-01', '%Y-%m-%d')
        
        # Obtain the ID from the dir name
        tiff_dir_path = dirname(raster_path)
        id = tiff_dir_path.split('/')[-1]
        
        # Instantiate pystac item
        item = pystac.Item(id=id,
                geometry=geom,
                bbox=bbox,
                datetime=time_acquired,
                properties=properties)
        
        # Get the item extension using the dataframe, from the raster path
        extensions = self._stac_dataframe[self._stac_dataframe['image'] == raster_path]['extensions'].values
        extensions = extensions[0] if extensions else None
        # Add the required extensions to the item
        if extensions:
            if isinstance(extensions, str):
                extensions = [extensions]
            for extension in extensions:
                extension_obj = self._extensions_dict[extension]
                extension_obj.add_extension_to_object(item)

        # Add the assets to the item
        # First of all, we need to get the image bands and extract them from the raster
        # in order to create the assets
        bands = self._stac_dataframe[self._stac_dataframe['image'] == raster_path]['bands'].values
        bands = bands[0] if bands else None
        with rasterio.open(raster_path) as raster:
            # TODO control in DEM data
            # TODO put this in a function
            if not bands:
                # If there is no bands, create a single band asset
                single_band = raster.read(1)
                band_name = f'{basename(raster_path)}.tiff'
                output_band = join(dirname(raster_path), band_name)
                # Copy the metadata
                metadata = raster.meta.copy()
                metadata.update({"count": 1})
                # Write the band to the output folder
                with rasterio.open(output_band, "w", **metadata) as dest:
                    dest.write(single_band, 1)
                # Instantiate pystac asset
                asset = pystac.Asset(href=band_name, title=band_name, media_type=pystac.MediaType.GEOTIFF)
                # Add the asset to the item
                item.add_asset(band_name, asset)
                # Add the required extensions to the asset if required
                if extensions:
                    if isinstance(extensions, str):
                        extensions = [extensions]
                    for extension in extensions:
                        extension_obj = self._extensions_dict[extension]
                        extension_obj.add_extension_to_object(asset)
            else:
                for band in bands:
                    i = bands.index(band)
                    single_band = raster.read(i + 1)
                    band_name = f'{band}.tiff'
                    output_band = join(dirname(raster_path), band_name)
                    # Copy the metadata
                    metadata = raster.meta.copy()
                    metadata.update({"count": 1})
                    # Write the band to the output folder
                    with rasterio.open(output_band, "w", **metadata) as dest:
                        dest.write(single_band, 1)
                    # Instantiate pystac asset
                    asset = pystac.Asset(href=band_name, title=band, media_type=pystac.MediaType.GEOTIFF)
                    # Add the asset to the item
                    item.add_asset(band_name, asset)
                    # Add the required extensions to the asset if required
                    if extensions:
                        if isinstance(extensions, str):
                            extensions = [extensions]
                        for extension in extensions:
                            extension_obj = self._extensions_dict[extension]
                            extension_obj.add_extension_to_object(asset)

        return item

    def _get_item_metadata(self, raster_path: str) -> str:
        """
        Get the metadata JSON file of a given directory, associated to a raster file

        :param raster_path: path to the raster file
        """
        # Get the directory of the raster file
        raster_dir_path = dirname(raster_path)
        # Get the metadata JSON file
        # Check if there is a metadata.json file in the directory
        if 'metadata.json' in listdir(raster_dir_path):
            metadata_json = join(raster_dir_path, 'metadata.json')
        else:
            # If there is no metadata.json file in the directory, check if there is
            # a json file with the same name as the raster file
            raster_name = raster_path.split('/')[-1]
            raster_name = raster_name.split('.')[0]
            metadata_json = join(raster_dir_path, f'{raster_name}.json')
            if not exists(metadata_json):
                # If there is no metadata.json file in the directory, return None
                return None
        
        # Open the metadata.json file and return it
        with open(metadata_json, 'r') as f:
            metadata = json.load(f)
        
        return metadata
