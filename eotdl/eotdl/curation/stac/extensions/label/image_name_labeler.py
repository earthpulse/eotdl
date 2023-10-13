'''
Module for the STAC label extension ImageNameLabeler object
'''

import pystac
import pandas as pd
import json

from tqdm import tqdm
from os.path import join, dirname
from typing import List, Optional, Union
from ...extent import get_unknow_extent
from .base import LabelExtensionObject
from pystac.extensions.label import LabelExtension


class ImageNameLabeler(LabelExtensionObject):
    def __init__(self) -> None:
        super().__init__()

    def generate_stac_labels(
        self,
        catalog: Union[pystac.Catalog, str],
        stac_dataframe: Optional[pd.DataFrame] = None,
        collection: Optional[Union[pystac.Collection, str]] = 'source',
        label_description: Optional[str] = "Item label",
        label_type: Optional[str] = "vector",
        label_names: Optional[List[str]] = ["label"],
        **kwargs
    ) -> None:
        """
        Generate a labels collection from a STAC dataframe. 
        This class uses the label column of the dataframe as the label names.
        
        :param catalog: catalog to add the labels collection to
        :param stac_dataframe: dataframe with the STAC metadata of a given directory containing the assets to generate metadata
        :param collection: collection to add the labels collection to
        :param label_description: label description
        :param label_type: label type
        :param label_names: list of label names
        :param kwargs: optional arguments
            :param kwargs.label_properties: list of label properties
            :param kwargs.label_methods: list of label methods
            :param kwargs.label_tasks: list of label tasks
        """
        if stac_dataframe.empty:
            raise ValueError(
                "No STAC dataframe provided, please provide a STAC dataframe or generate it with <get_stac_dataframe> method"
            )
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

        # Generate the labels items
        print("Generating labels collection...")
        for source_item in tqdm(source_items):
            # There must be an item ID column in the STAC dataframe
            if not 'id' in stac_dataframe.columns:
                raise ValueError(
                    "No item ID column found in the STAC dataframe, please provide a STAC dataframe with the item ID column"
                )
            label_classes = stac_dataframe.label.unique().tolist()

            # Create the label item
            label_item = self.add_extension_to_item(
                source_item,
                label_description=label_description,
                label_type=label_type,
                label_names=[label_names],
                label_classes=[label_classes],
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
        except pystac.STACValidationError as e:
            raise pystac.STACError(f"Catalog validation error: {e}")
        
        # Add a GeoJSON FeatureCollection to every label item, as recommended by the spec
        # https://github.com/stac-extensions/label#assets
        self.add_geojson_to_items(collection, 
                                  stac_dataframe,
                                  label_type=label_type)
        catalog.normalize_and_save(dirname(catalog.get_self_href()), pystac.CatalogType.SELF_CONTAINED)
        print('Success on labels generation!')

    def add_geojson_to_items(self, 
                             collection: pystac.Collection,
                             df: pd.DataFrame,
                             label_type: str
                             ) -> None:
        """
        Add a GeoJSON FeatureCollection to every label item, as recommended by the spec
        https://github.com/stac-extensions/label#assets

        :param collection: collection to add the labels collection to
        :param df: dataframe with the STAC metadata of a given directory containing the assets to generate metadata
        :param label_type: label type
        """
        for item in collection.get_all_items():
            geojson_path = join(dirname(item.get_self_href()), f'{item.id}.geojson')

            properties = {'roles': ['labels', f'labels-{label_type}']}

            # TODO depending on the tasks, there must be extra fields
            # https://github.com/stac-extensions/label#assets
            tasks = item.properties['label:tasks']
            if 'tile_regression' in tasks:
                pass
            elif any(task in tasks for task in ('tile_classification', 'object_detection', 'segmentation')):
                pass

            label_ext = LabelExtension.ext(item)
            label_ext.add_geojson_labels(href=geojson_path, 
                                         title='Label', 
                                         properties=properties)
            item.make_asset_hrefs_relative()
            
            item_id = item.id
            geometry = item.geometry
            labels = [df[df['id'] == item_id]['label'].values[0]]
            # There is data like DEM data that does not have datetime but start and end datetime
            datetime = item.datetime.isoformat() if item.datetime else (item.properties.start_datetime.isoformat(),
                                                                        item.properties.end_datetime.isoformat())
            labels_properties = dict(zip(item.properties['label:properties'], labels)) if label_type == 'vector' else dict()
            labels_properties['datetime'] = datetime

            geojson = {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": geometry,
                        "properties": labels_properties,
                    }
                ],
            }

            with open(geojson_path, "w") as f:
                json.dump(geojson, f)
