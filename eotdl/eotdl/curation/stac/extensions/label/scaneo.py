'''
Module for the STAC label extension ScaneoLabeler object
'''

import pystac
import pandas as pd
import json

from glob import glob
from tqdm import tqdm
from os.path import join, dirname, exists, splitext, basename, abspath
from typing import List, Optional, Union
from pystac.extensions.label import LabelExtension

from .base import LabelExtensionObject
from ...extent import get_unknow_extent


class ScaneoLabeler(LabelExtensionObject):
    def __init__(self) -> None:
        super().__init__()

    def generate_stac_labels(
        self,
        catalog: Union[pystac.Catalog, str],
        root_folder: str,
        collection: Optional[Union[pystac.Collection, str]] = 'source',
        label_description: Optional[str] = "Item label",
        label_type: Optional[str] = "vector",
        label_names: Optional[List[str]] = ["label"],
        **kwargs
    ) -> None:
        """
        Generate a labels collection from a STAC dataframe. 
        This class should be used when the items have been labeled using SCANEO, as is implemented
        taking into account the SCANEO labeling format.
        
        :param catalog: catalog to add the labels collection to
        :param root_folder: root folder where are the images and the labels as GeoJSON files, following the SCANEO labeling format
        :param stac_dataframe: dataframe with the STAC metadata of a given directory containing the assets to generate metadata
        :param collection: collection to add the labels collection to
        :param label_description: label description
        :param label_type: label type
        :param label_names: list of label names
        :param kwargs: optional arguments
            :param kwargs.label_properties: list of label properties
            :param kwargs.label_methods: list of label methods
        """
        if isinstance(catalog, str):
            catalog = pystac.Catalog.from_file(catalog)

        # Add the labels collection to the catalog
        # If exists a source collection, get it extent
        source_collection = catalog.get_child(collection)
        if source_collection:
            extent = source_collection.extent
            source_items = source_collection.get_stac_objects(pystac.RelType.ITEM)
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

        # Get the GeoJSON files
        geojson_files = glob(join(root_folder, "*.geojson"))
        if not geojson_files:
            raise ValueError(
                "No GeoJSON files found in the root folder, please provide a root folder with the GeoJSON files"
            )

        # Get the label classes
        label_classes = self.get_label_classes(root_folder, geojson_files)

        # Generate the labels items
        for source_item in tqdm(source_items, desc="Generating labels collection..."):
            # Get the GeoJSON label of the item
            geojson_label = self.get_geojson_of_item(source_item, geojson_files)
            # Get the tasks from the GeoJSON label
            tasks = self.get_tasks_from_geojson(geojson_label)
            # Add the tasks to the kwargs
            kwargs['label_tasks'] = tasks

            # Create the label item
            label_item = self.add_extension_to_item(
                source_item,
                label_description=label_description,
                label_type=label_type,
                label_names=label_names,
                label_classes=label_classes,
                **kwargs
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
            # Match the GeoJSON label with the label item
            self.add_geojson_to_item(label_item, geojson_label, label_type)
            # Add the item to the collection
            collection.add_item(label_item)

        # Add the extension to the collection
        self.add_extension_to_collection(
            collection,
            label_names=[label_names],
            label_classes=[label_classes],
            label_type=label_type,
        )

        # Validate and save the catalog
        # Before adding the geojson, we need to save the catalog
        # and then iterate over the items to add the geojson
        try:
            pystac.validation.validate(catalog)
            catalog.normalize_and_save(dirname(catalog.get_self_href()), pystac.CatalogType.SELF_CONTAINED)
            print('Success on labels generation!')
        except pystac.STACValidationError as e:
            raise pystac.STACError(f"Catalog validation error: {e}")

    def add_geojson_to_item(self, 
                            item: pystac.Item,
                            geojson_path: str,
                            label_type: str
                            ) -> None:
        """
        Add a GeoJSON FeatureCollection to every label item, as recommended by the spec
        https://github.com/stac-extensions/label#assets

        :param collection: collection to add the labels collection to
        :param df: dataframe with the STAC metadata of a given directory containing the assets to generate metadata
        :param label_type: label type
        """
        properties = {'roles': ['labels', f'labels-{label_type}']}

        label_ext = LabelExtension.ext(item, add_if_missing=True)
        item.make_asset_hrefs_absolute()
        label_ext.add_geojson_labels(href=abspath(geojson_path), 
                                     title='Label', 
                                     properties=properties)
        item.make_asset_hrefs_relative()
        
    def get_label_classes(self,
                          root_folder: str,
                          geojsons: List[str]
                          ) -> List[str]:
        """
        Get the label classes from the labels.json file if exists, or from the GeoJSON files instead
        """
        label_classes = list()

        labels_json = glob(join(root_folder, "labels.json"))[0]
        if exists(labels_json):
            with open(labels_json, 'r') as f:
                labels = json.load(f)
            for value in labels['labels']:
                label_classes.append(value['name']) if value['name'] not in label_classes else None
        else:
            for geojson in geojsons:
                with open(geojson, 'r') as f:
                    labels = json.load(f)
                for value in labels['features']:
                    label_classes.append(value['properties']['labels']) if value['properties']['labels'] not in label_classes else None

        return [label_classes]

    def get_geojson_of_item(self,
                            item: pystac.Item,
                            geojsons: List[str]
                            ) -> str:
        """
        Get the GeoJSON label of the item from a list of GeoJSON files

        :param item: item to get the GeoJSON label
        :param geojsons: list of GeoJSON files

        :return: path to the GeoJSON label of the item
        """
        item_id = item.id
        # Get a dict with <geojson_filename>: <geojson_path>, as the geojson_filename
        # must match the item ID
        geojsons_dict = dict(zip([splitext(basename(geojson))[0] for geojson in geojsons], geojsons))
        geojson_path = geojsons_dict.get(item_id)
        
        return geojson_path

    def get_tasks_from_geojson(self, 
                               geojson_path: str
                               ) -> List[str]:
        """
        Get the tasks from the GeoJSON label

        :param geojson_path: path to the GeoJSON label

        :return: list of tasks
        """
        with open(geojson_path, 'r') as f:
            geojson = json.load(f)
            tasks = list()
            for feature in geojson['features']:
                for task in feature['properties']['tasks']:
                    tasks.append(task) if task not in tasks else None
        
        return tasks
