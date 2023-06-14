"""
Module for generating STAC metadata 
"""

import pandas as pd
import json
import pystac
from random import sample

from os import listdir
from os.path import join, basename, exists, dirname

import rasterio
from rasterio.warp import transform_bounds

from datetime import datetime
from shapely.geometry import Polygon, mapping
from glob import glob

from stac_validator.stac_validator import StacValidate

from .parsers import STACIdParser, StructuredParser
from .utils import format_time_acquired, count_ocurrences
from .extensions import type_stac_extensions_dict


class STACGenerator:
        
    def __init__(self, 
                 image_format: str='tiff',
                 catalog_type: pystac.CatalogType=pystac.CatalogType.SELF_CONTAINED, 
                 item_parser: STACIdParser=StructuredParser
                 ) -> None:
        """
        Initialize the STAC generator
        
        :param image_format: image format of the assets
        :param catalog_type: type of the catalog
        :param item_parser: parser to get the item ID
        """
        self._image_format = image_format
        self._catalog_type = catalog_type
        self._item_parser = item_parser()
        self._extensions_dict: dict = type_stac_extensions_dict
        self._validator = StacValidate(extensions=True)
        self._stac_dataframe = None

    def generate_stac_metadata(self,
                               stac_dataframe: pd.DataFrame,
                               id: str,
                               description: str,
                               output_folder: str='stac',
                               kwargs: dict={}) -> None:
        """
        Generate STAC metadata for a given directory containing the assets to generate metadata

        :param stac_dataframe: dataframe with the STAC metadata of a given directory containing the assets to generate metadata
        :param id: id of the catalog
        :param description: description of the catalog
        :param output_folder: output folder to write the catalog to
        """
        self._stac_dataframe = stac_dataframe
        
        # Create an empty catalog
        catalog = self.create_stac_catalog(id=id, description=description)
        
        # Add the collections to the catalog
        collections = self._stac_dataframe.collection.unique()
        for collection_path in collections:
            # TODO check if the items are directly under the root directory
            # Generate the collection
            collection = self.generate_stac_collection(collection_path)
            # Add the collection to the catalog
            catalog.add_child(collection)
        
        # Add the catalog to the root directory
        catalog.normalize_hrefs(output_folder)

        # Validate the catalog
        try:
            pystac.validation.validate(catalog)
            catalog.save(catalog_type=self._catalog_type)
        except pystac.STACValidationError as e:
            print(f'Catalog validation error: {e}')
            return

    def get_stac_dataframe(self, path: str, bands: dict=None, extensions: dict=None) -> pd.DataFrame:
        """
        Get a dataframe with the STAC metadata of a given directory containing the assets to generate metadata

        :param path: path to the root directory
        :param extensions: dictionary with the extensions
        :param image_format: image format of the assets
        """
        images = glob(str(path) + f'/**/*.{self._image_format}', recursive=True)
        images = sample(images, 50)   # TODO drop this line
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

        images_dirs = [dirname(i) for i in images]

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
        Get a list of items from a dictionary

        :param labels: list of labels
        :param items: dictionary with the items
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
                    spatial_extent = pystac.SpatialExtent([[0, 0, 0, 0]])
                    return spatial_extent
                bboxes.append(bbox)
        # Get the minimum and maximum values of the bounding boxes
        try:
            left = min([bbox[0] for bbox in bboxes])
            bottom = min([bbox[1] for bbox in bboxes])
            right = max([bbox[2] for bbox in bboxes])
            top = max([bbox[3] for bbox in bboxes])
            spatial_extent = pystac.SpatialExtent([[left, bottom, right, top]])
        except ValueError:
            spatial_extent = pystac.SpatialExtent([[0, 0, 0, 0]])
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
            return self._get_unknow_temporal_interval()
        
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
        else:
            return self._get_unknow_temporal_interval()

        return temporal_interval
    
    def _get_unknow_temporal_interval(self) -> pystac.TemporalExtent:
        """
        Get an unknown temporal interval
        """
        min_date = datetime.strptime('2000-01-01', '%Y-%m-%d')
        max_date = datetime.strptime('2023-12-31', '%Y-%m-%d')

        return pystac.TemporalExtent([min_date, max_date])

    def create_stac_catalog(self, id: str, description: str, kwargs: dict={}) -> pystac.Catalog:
        """
        Create a STAC catalog

        :param id: id of the catalog
        :param description: description of the catalog
        :param params: additional parameters
        """
        return pystac.Catalog(id=id, description=description, **kwargs)

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

    def create_stac_collection(self, id: str, description: str, extent: pystac.Extent, kwargs: dict={}) -> pystac.Collection:
        """
        Create a STAC collection

        :param id: id of the collection
        :param description: description of the collection
        :param extent: extent of the collection
        :param params: additional parameters
        """
        return pystac.Collection(id=id, description=description, extent=extent, **kwargs)

    def create_stac_item(self,
                        raster_path: str,
                        kwargs: dict={}
                        ) -> pystac.Item:
        """
        Create a STAC item from a directory containing the raster files and the metadata.json file

        :param raster_path: path to the raster file
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
                # If the raster has no crs, set the bounding box to 0
                left, bottom, right, top = 0, 0, 0, 0

        # Create bbox
        bbox = [left, bottom, right, top]

        # Create geojson feature
        # If the bounding box has no values, set the geometry to None
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
        
        # Obtain the item ID. The approach depends on the item parser
        id = self._item_parser.get_item_id(raster_path)
        
        # Instantiate pystac item
        item = pystac.Item(id=id,
                geometry=geom,
                bbox=bbox,
                datetime=time_acquired,
                properties=properties,
                **kwargs)
        
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
        if not bands:
            # If there is no bands, create a single band asset from the file, assuming thats a singleband raster
            href = basename(raster_path)
            title = basename(raster_path).split('.')[0]
            asset = pystac.Asset(href=href, title=title, media_type=pystac.MediaType.GEOTIFF)
        else:
            with rasterio.open(raster_path, 'r') as raster:
                # Get the name of the raster file without extension
                raster_name = basename(raster_path).split('.')[0]
                if isinstance(bands, str):
                    bands = [bands]
                for band in bands:
                    i = bands.index(band)
                    try:
                        single_band = raster.read(i + 1)
                    except IndexError:
                        # TODO put try here for IndexError: band index 2 out of range (not in (1,))
                        # TODO control
                        single_band = raster.read(1)
                    band_name = f'{raster_name}_{band}.{self._image_format}'
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
