"""
Module for generating STAC metadata 
"""

import traceback
from typing import Union
import pandas as pd
import pystac
from tqdm import tqdm

from os.path import join, basename, dirname
from shutil import rmtree

import rasterio
import random
from rasterio.warp import transform_bounds
from typing import Union, List

from datetime import datetime
from shapely.geometry import Polygon, mapping
from glob import glob
from typing import Union, Optional

from .parsers import STACIdParser, StructuredParser
from .assets import STACAssetGenerator
from .dataframe_labeling import LabelingStrategy, UnlabeledStrategy
from .utils import (format_time_acquired, 
                    cut_images, 
                    get_item_metadata,
                    get_all_images_in_path)
from .extensions import (type_stac_extensions_dict, 
                         SUPPORTED_EXTENSIONS, 
                         LabelExtensionObject)
from .extent import (get_unknow_extent, 
                     get_collection_extent)


class STACGenerator:
    def __init__(
        self,
        image_format: str = "tiff",
        catalog_type: pystac.CatalogType = pystac.CatalogType.SELF_CONTAINED,
        item_parser: STACIdParser = StructuredParser,
        assets_generator: STACAssetGenerator = STACAssetGenerator,
        labeling_strategy: LabelingStrategy = UnlabeledStrategy,
    ) -> None:
        """
        Initialize the STAC generator

        :param image_format: image format of the assets
        :param catalog_type: type of the catalog
        :param item_parser: parser to get the item ID
        :param assets_generator: generator to generate the assets
        :param labeling_strategy: strategy to label the images
        """
        self._image_format = image_format
        self._catalog_type = catalog_type
        self._item_parser = item_parser()
        self._assets_generator = assets_generator()
        self._labeling_strategy = labeling_strategy()
        self._extensions_dict: dict = type_stac_extensions_dict
        self._stac_dataframe = pd.DataFrame()

    def generate_stac_metadata(
        self,
        id: str,
        description: str,
        stac_dataframe: pd.DataFrame = None,
        output_folder: str = "stac",
        kwargs: dict = {},
    ) -> None:
        """
        Generate STAC metadata for a given directory containing the assets to generate metadata

        :param id: id of the catalog
        :param description: description of the catalog
        :param stac_dataframe: dataframe with the STAC metadata of a given directory containing the assets to generate metadata
        :param output_folder: output folder to write the catalog to
        """
        self._stac_dataframe = (
            stac_dataframe if self._stac_dataframe.empty else self._stac_dataframe
        )
        if self._stac_dataframe.empty:
            raise ValueError("No STAC dataframe provided")

        # Create an empty catalog
        catalog = pystac.Catalog(id=id, description=description, **kwargs)
        
        # Add the collections to the catalog
        collections = self._stac_dataframe.collection.unique()
        for collection_path in collections:
            # Generate the collection
            collection = self.generate_stac_collection(collection_path)
            # Add the collection to the catalog
            catalog.add_child(collection)

        # Check there have been generate all the items from the images
        items_count = 0
        for collection in catalog.get_children():
            items = list(set([item.id for item in collection.get_items(recursive=True)]))
            items_count += len(items)
        if len(self._stac_dataframe) != items_count:
            raise pystac.STACError(
                "Not all the STAC items have been generated, please check the Item parser or the STAC dataframe. If you are using the StructuredParser, check that the images are in the correct folder structure."
            )

        # Add the catalog to the root directory
        catalog.normalize_hrefs(output_folder)

        # Validate the catalog
        print("Validating and saving catalog...")
        try:
            pystac.validation.validate(catalog)
            catalog.save(catalog_type=self._catalog_type)
            print("Success!")
        except pystac.STACValidationError as e:
            print(f"Catalog validation error: {e}")
            return

    def get_stac_dataframe(self, 
                           path: str, 
                           collections: Optional[Union[str, dict]]='source',
                           bands: Optional[dict]=None, 
                           extensions: Optional[dict]=None,
                           sample: Optional[int]=None
                           ) -> pd.DataFrame:
        """
        Get a dataframe with the STAC metadata of a given directory containing the assets to generate metadata

        :param path: path to the root directory
        :param collections: dictionary with the collections
        :param bands: dictionary with the bands
        :param extensions: dictionary with the extensions
        """
        images = get_all_images_in_path(path, self._image_format)
        if len(images) == 0:
            raise ValueError("No images found in the given path with the given extension. Please check the path and the extension")
        
        if self._assets_generator.type == 'Extracted':
            images = cut_images(images)

        if sample:
            try:
                images = random.sample(images, sample)
            except ValueError:
                raise ValueError(f"Sample size must be smaller than the number of images ({len(images)}). May be there are no images found in the given path with the given extension")

        labels, ixs = self._labeling_strategy.get_images_labels(images)
        bands_values = self._get_items_list_from_dict(labels, bands)
        extensions_values = self._get_items_list_from_dict(labels, extensions)

        if collections == "source":
            # List of path with the same value repeated as many times as the number of images
            collections_values = [join(path, "source") for i in range(len(images))]
        elif collections == '*':
            collections_values = [join(path, basename(dirname(image))) for image in images]
        else:
            try:
                collections_values = [join(path, value) for value in self._get_items_list_from_dict(labels, collections)]
            except TypeError:
                raise pystac.STACError('There is an error generating the collections. Please check the collections dictionary')

        df = pd.DataFrame({'image': images, 
                           'label': labels, 
                           'ix': ixs, 
                           'collection': collections_values, 
                           'extensions': extensions_values, 
                           'bands': bands_values
                           })
        
        self._stac_dataframe = df

        return df

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

    def generate_stac_collection(self, collection_path: str) -> pystac.Collection:
        """
        Generate a STAC collection from a directory containing the assets to generate metadata

        :param collection_path: path to the collection
        """
        # Get the images of the collection, as they are needed to obtain the collection extent
        collection_images = self._stac_dataframe[
            self._stac_dataframe["collection"] == collection_path
        ]["image"]
        # Get the collection extent
        extent = get_collection_extent(collection_images)
        # Create the collection
        collection_id = basename(collection_path)
        collection = pystac.Collection(
            id=collection_id, description="Collection", extent=extent
        )

        print(f"Generating {collection_id} collection...")
        for image in tqdm(collection_images):
            # Create the item
            item = self.create_stac_item(image)
            # Add the item to the collection
            collection.add_item(item)

        # Return the collection
        return collection

    def create_stac_item(self, raster_path: str, kwargs: dict = {}) -> pystac.Item:
        """
        Create a STAC item from a directory containing the raster files and the metadata.json file

        :param raster_path: path to the raster file
        """
        # Check if there is any metadata file in the directory associated to the raster file
        metadata = get_item_metadata(raster_path)

        # Obtain the bounding box from the raster
        with rasterio.open(raster_path) as ds:
            bounds = ds.bounds
            dst_crs = "EPSG:4326"
            try:
                left, bottom, right, top = rasterio.warp.transform_bounds(
                    ds.crs, dst_crs, *bounds
                )
            except rasterio.errors.CRSError:
                # If the raster has no crs, set the bounding box to 0
                left, bottom, right, top = 0, 0, 0, 0

        # Create bbox
        bbox = [left, bottom, right, top]

        # Create geojson feature
        # If the bounding box has no values, set the geometry to None
        geom = mapping(
            Polygon([[left, bottom], [left, top], [right, top], [right, bottom]])
        )

        # Initialize pySTAC item parameters
        params = dict()
        params["properties"] = dict()

        # Obtain the date acquired
        start_time, end_time = None, None
        if metadata and metadata["acquisition-date"] and metadata["type"] not in ('dem', 'DEM'):
            time_acquired = format_time_acquired(metadata["acquisition-date"])
        else:
            # Check if the type of the data is DEM
            if metadata and metadata["type"] and metadata["type"] in ("dem", "DEM"):
                time_acquired = None
                start_time = datetime.strptime("2011-01-01", "%Y-%m-%d")
                end_time = datetime.strptime("2015-01-07", "%Y-%m-%d")
                params["start_datetime"] = start_time
                params["end_datetime"] = end_time
            else:
                # Set unknown date
                time_acquired = datetime.strptime("2000-01-01", "%Y-%m-%d")

        # Obtain the item ID. The approach depends on the item parser
        id = self._item_parser.get_item_id(raster_path)
        # Add the item ID to the dataframe, to be able to get it later
        self._stac_dataframe.loc[
            self._stac_dataframe["image"] == raster_path, "id"
        ] = id
        
        # Instantiate pystac item
        item = pystac.Item(
            id=id, geometry=geom, bbox=bbox, datetime=time_acquired, **params
        )

        # Get the item info, from the raster path
        item_info = self._stac_dataframe[self._stac_dataframe["image"] == raster_path]
        # Get the extensions of the item
        extensions = item_info["extensions"].values
        extensions = extensions[0] if extensions else None

        # Add the required extensions to the item
        if extensions:
            if isinstance(extensions, str):
                extensions = [extensions]
            for extension in extensions:
                if extension not in SUPPORTED_EXTENSIONS:
                    raise ValueError(f"Extension {extension} not supported")
                else:
                    extension_obj = self._extensions_dict[extension]
                    extension_obj.add_extension_to_object(item, item_info)

        # Add the assets to the item
        assets = self._assets_generator.extract_assets(item_info)
        if not assets:
            # If there are not assets using the selected generator, try with the default
            assets = STACAssetGenerator.extract_assets(item_info)

        # Add the assets to the item
        if assets:
            for asset in assets:
                if isinstance(asset, pystac.Asset):
                    item.add_asset(asset.title, asset)
                    # Add the required extensions to the asset if required
                    if extensions:
                        if isinstance(extensions, str):
                            extensions = [extensions]
                        for extension in extensions:
                            if extension not in SUPPORTED_EXTENSIONS:
                                raise ValueError(f"Extension {extension} not supported")
                            else:
                                extension_obj = self._extensions_dict[extension]
                                extension_obj.add_extension_to_object(asset, item_info)
        item.set_self_href(join(dirname(raster_path), f"{id}.json"))
        item.make_asset_hrefs_relative()
        return item
