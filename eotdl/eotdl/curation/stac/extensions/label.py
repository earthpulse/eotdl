'''
Module for Label STAC extensions object
'''

import pystac
import json
import pandas as pd

from os.path import join, dirname
from typing import List, Optional, Union
from .base import STACExtensionObject
from pystac.extensions.label import (LabelClasses, LabelExtension, SummariesLabelExtension)


class LabelExtensionObject(STACExtensionObject):
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def add_extension_to_item(
        self,
        obj: pystac.Item,
        label_description: str,
        label_type: str,
        label_names: List[str],
        label_classes: List[str],
        **kwargs
    ) -> Union[pystac.Item, pystac.Asset]:
        """
        Add the extension to the given object

        :param obj: object to add the extension
        :param label_description: label description
        :param label_type: label type
        :param label_names: list of label names
        :param label_classes: list of label classes of the item
        :param kwargs: optional arguments
            :param kwargs.label_properties: list of label properties
            :param kwargs.label_methods: list of label methods
            :param kwargs.label_tasks: list of label tasks

        :return: the item with the label extension
        """
        label_item = pystac.Item(id=obj.id,
                                 geometry=obj.geometry,
                                 bbox=obj.bbox,
                                 properties=dict(),
                                 datetime=obj.datetime
                                 )
        
        # Add the label extension to the item
        LabelExtension.add_to(label_item)

        # Access the label extension
        label_ext = LabelExtension.ext(label_item)

        # Add the label classes
        for name, classes in zip(label_names, label_classes):
            label_classes = LabelClasses.create(
                name=name,
                classes=classes,
            )
            label_ext.label_classes = [label_classes]

        # Add the label description
        label_ext.label_description = label_description
        # Add the label type
        label_ext.label_type = label_type
        # Add the label properties, if any
        label_ext.label_properties = kwargs.get('label_properties') if kwargs.get('label_properties', None) else None
        # Add the label methods, if any
        label_ext.label_methods = kwargs.get('label_methods') if kwargs.get('label_methods', None) else None
        # Add the label tasks, if any
        label_ext.label_tasks = kwargs.get('label_tasks') if kwargs.get('label_tasks', None) else None
        # Add the source
        label_ext.add_source(obj)

        return label_item
    
    @classmethod
    def add_geojson_to_items(self, 
                             collection: pystac.Collection,
                             df: pd.DataFrame
                             ) -> None:
        """
        """
        for item in collection.get_all_items():
            geojson_path = join(dirname(item.get_self_href()), f'{item.id}.geojson')

            properties = {'roles': ['labels', f'labels-vector']}

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
            labels_properties = dict(zip(item.properties['label:properties'], labels))
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

    @classmethod
    def add_extension_to_collection(
            self,
            obj: pystac.Collection,
            label_names: List[str],
            label_classes: List[Union[list, tuple]],
            label_type: str
    ) -> None:
        """
        Add the label extension to the given collection

        :param obj: object to add the extension
        :param label_names: list of label names
        :param label_classes: list of label classes
        :param label_type: label type
        """
        LabelExtension.add_to(obj)

        # Add the label extension to the collection
        label_ext = SummariesLabelExtension(obj)

        # Add the label classes
        for name, classes in zip(label_names, label_classes):
            label_classes = LabelClasses.create(
                name=name,
                classes=classes,
            )
            label_ext.label_classes = [label_classes]

        # Add the label type
        label_ext.label_type = label_type
