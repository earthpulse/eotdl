"""
Module for generating STAC metadata 
"""

from typing import Union
import pandas as pd
import pystac
from tqdm import tqdm

from os.path import join, basename, dirname
from shutil import rmtree

import rasterio
from rasterio.warp import transform_bounds
from typing import Union, List

from datetime import datetime
from shapely.geometry import Polygon, mapping
from glob import glob
from typing import Union, Optional

from .parsers import STACIdParser, StructuredParser
from .assets import STACAssetGenerator
from .utils import (format_time_acquired, 
                    cut_images, 
                    get_item_metadata)
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
    ) -> None:
        """
        Initialize the STAC generator

        :param image_format: image format of the assets
        :param catalog_type: type of the catalog
        :param item_parser: parser to get the item ID
        :param assets_generator: generator to generate the assets
        """
        self._image_format = image_format
        self._catalog_type = catalog_type
        self._item_parser = item_parser()
        self._assets_generator = assets_generator()
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
            # TODO check if the items are directly under the root directory
            # Generate the collection
            collection = self.generate_stac_collection(collection_path)
            # Add the collection to the catalog
            catalog.add_child(collection)

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
                           collections: Union[str, dict]='source',
                           bands: dict=None, 
                           extensions: dict=None
                           ) -> pd.DataFrame:
        """
        Get a dataframe with the STAC metadata of a given directory containing the assets to generate metadata

        :param path: path to the root directory
        :param collections: dictionary with the collections
        :param bands: dictionary with the bands
        :param extensions: dictionary with the extensions
        """
        images = glob(str(path) + f'/**/*.{self._image_format}', recursive=True)
        if self._assets_generator.type == 'Extracted':
            images = cut_images(images)

        labels, ixs = self._format_labels(images)
        bands_values = self._get_items_list_from_dict(labels, bands)
        extensions_values = self._get_items_list_from_dict(labels, extensions)

        if collections == "source":
            # List of path with the same value repeated as many times as the number of images
            collections_values = [join(path, "source") for i in range(len(images))]
        else:
            try:
                collections_values = [join(path, value) for value in self._get_items_list_from_dict(labels, collections)]
            except TypeError as e:
                # TODO control this error
                raise TypeError(f'Control this error')

        df = pd.DataFrame({'image': images, 
                           'label': labels, 
                           'ix': ixs, 
                           'collection': collections_values, 
                           'extensions': extensions_values, 
                           'bands': bands_values
                           })
        
        self._stac_dataframe = df

        return df
    
    def _format_labels(self, images):
        """
        Format the labels of the images

        :param images: list of images
        """
        labels = [x.split("/")[-1].split("_")[0].split(".")[0] for x in images]
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
        if metadata and metadata["date-adquired"] and metadata["type"] not in ('dem', 'DEM'):
            time_acquired = format_time_acquired(metadata["date-adquired"])
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

    def generate_stac_labels(
        self,
        catalog: Union[pystac.Catalog, str],
        stac_dataframe: Optional[pd.DataFrame] = None,
        collection: Optional[Union[pystac.Collection, str]] = None,
    ) -> None:
        """
        Generate a labels collection from a STAC dataframe
        
        :param catalog: catalog to add the labels collection to
        :param stac_dataframe: dataframe with the STAC metadata of a given directory containing the assets to generate metadata
        :param collection: collection to add the labels collection to
        """
        self._stac_dataframe = (
            stac_dataframe if self._stac_dataframe.empty else self._stac_dataframe
        )
        if self._stac_dataframe.empty:
            raise ValueError(
                "No STAC dataframe provided, please provide a STAC dataframe or generate it with <get_stac_dataframe> method"
            )
        if isinstance(catalog, str):
            catalog = pystac.Catalog.from_file(catalog)

        # Add the labels collection to the catalog
        # If exists a source collection, get it extent
        source_collection = catalog.get_child("source")
        if source_collection:
            extent = source_collection.extent
            source_items = source_collection.get_all_items()
        else:
            if not collection:
                raise ValueError(
                    "No source collection provided, please provide a source collection"
                )
            extent = get_unknow_extent()

        # Create the labels collection and add it to the catalog if it does not exist
        # If it exists, remove it
        collection = pystac.Collection(id="labels", description="Labels", extent=extent)
        if collection.id in [c.id for c in catalog.get_children()]:
            catalog.remove_child(collection.id)
        catalog.add_child(collection)

        # Generate the labels items
        print("Generating labels collection...")
        for source_item in tqdm(source_items):
            # There must be an item ID column in the STAC dataframe
            if not 'id' in self._stac_dataframe.columns:
                raise ValueError(
                    "No item ID column found in the STAC dataframe, please provide a STAC dataframe with the item ID column"
                )
            label_classes = self._stac_dataframe.label.unique().tolist()

            # Create the label item
            # TODO put in kwargs
            label_item = LabelExtensionObject.add_extension_to_item(
                source_item,
                label_names=["label"],
                label_classes=[label_classes],
                label_properties=["label"],
                label_description="Item label",
                label_methods=["manual"],
                label_tasks=["classification"],
                label_type="vector"
            )
            # Add the self href to the label item, following the Best Practices Layout
            # https://github.com/radiantearth/stac-spec/blob/master/best-practices.md
            label_item.set_self_href(
                join(
                    dirname(collection.get_self_href()),
                    label_item.id,
                    f"{label_item.id}.json"
                    )
            )
            collection.add_item(label_item)

        # Add the extension to the collection
        # TODO put in kwargs
        LabelExtensionObject.add_extension_to_collection(
            collection,
            label_names=["label"],
            label_classes=[label_classes],
            label_type="vector",
        )

        # Validate and save the catalog
        # Before adding the geojson, we need to save the catalog
        # and then iterate over the items to add the geojson
        try:
            pystac.validation.validate(catalog)
            catalog.normalize_and_save(dirname(catalog.get_self_href()), self._catalog_type)
        except pystac.STACValidationError as e:
            print(f"Catalog validation error: {e}")
            return
        
        # Add a GeoJSON FeatureCollection to every label item, as recommended by the spec
        # https://github.com/stac-extensions/label#assets
        LabelExtensionObject.add_geojson_to_items(collection, 
                                                  self._stac_dataframe)
        catalog.normalize_and_save(dirname(catalog.get_self_href()), self._catalog_type)


def merge_stac_catalogs(catalog_1: Union[pystac.Catalog, str],
                        catalog_2: Union[pystac.Catalog, str],
                        destination: Optional[str] = None,
                        keep_extensions: Optional[bool] = False,
                        catalog_type: Optional[pystac.CatalogType] = pystac.CatalogType.SELF_CONTAINED
                        ) -> None:
    """
    Merge two STAC catalogs, keeping the properties, collection and items of both catalogs

    :param catalog_1: first catalog to merge
    :param catalog_2: second catalog to merge
    :param destination: destination folder to save the merged catalog
    :param keep_extensions: keep the extensions of the first catalog
    :param catalog_type: type of the catalog
    """
    if isinstance(catalog_1, str):
        catalog_1 = pystac.Catalog.from_file(catalog_1)
    if isinstance(catalog_2, str):
        catalog_2 = pystac.Catalog.from_file(catalog_2)

    for col1 in tqdm(catalog_1.get_children(), desc='Merging catalogs...'):
        # Check if the collection exists in catalog_2
        col2 = catalog_2.get_child(col1.id)
        if col2 is None:
            # If it does not exist, add it
            col1_ = col1.clone()
            catalog_2.add_child(col1)
            col2 = catalog_2.get_child(col1.id)
            col2.clear_items()
            for i in col1_.get_all_items():
                col2.add_item(i)
        else:
            # If it exists, merge the items
            for item1 in col1.get_items():
                if col2.get_item(item1.id) is None:
                    col2.add_item(item1)

    if keep_extensions:
        for ext in catalog_1.stac_extensions:
            if ext not in catalog_2.stac_extensions:
                catalog_2.stac_extensions.append(ext)

        for extra_field_name, extra_field_value in catalog_1.extra_fields.items():
            if extra_field_name not in catalog_2.extra_fields:
                catalog_2.extra_fields[extra_field_name] = extra_field_value

    if not destination:
        destination = dirname(catalog_2.get_self_href())
        rmtree(destination)   # Remove the old catalog and replace it with the new one
    # Save the merged catalog
    print('Validating...')
    catalog_2.normalize_and_save(destination, catalog_type)
    print('Success')
