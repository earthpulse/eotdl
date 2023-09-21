'''
STAC utils
'''

import pystac

from os.path import dirname, join, abspath
from typing import Union, Optional
from tqdm import tqdm
from traceback import print_exc
from shutil import rmtree


def get_all_children(obj: pystac.STACObject) -> list:
    """
    Get all the children of a STAC object

    :param obj: STAC object
    """
    children = []
    # Append the current object to the list
    children.append(obj.to_dict())

    # Collections
    collections = list(obj.get_collections())

    for collection in collections:
        children.append(collection.to_dict())

    # Items
    items = obj.get_items()
    for item in items:
        children.append(item.to_dict())

    # Items from collections
    for collection in collections:
        items = collection.get_items()
        for item in items:
            children.append(item.to_dict())

    return children


def make_links_relative_to_path(path: str,
                                catalog: Union[pystac.Catalog, str],
                                ) -> pystac.Catalog:
    """
    Makes all asset HREFs in the catalog relative to a given path

    :param path: path to make the links relative
    :param catalog: catalog to make the links relative

    :return: catalog with the links relative
    """
    if isinstance(catalog, str):
        catalog = pystac.read_file(catalog)
    path = abspath(path)

    catalog.make_all_asset_hrefs_absolute()

    for collection in catalog.get_children():
        new_collection = collection.clone()
        new_collection.set_self_href(join(path, collection.id, f"collection.json"))
        new_collection.set_root(catalog)
        new_collection.set_parent(catalog)
        catalog.remove_child(collection.id)
        catalog.add_child(new_collection)
        for item in collection.get_all_items():
            new_item = item.clone()
            new_item.set_self_href(join(path, item.id, f"{item.id}.json"))
            new_item.set_parent(collection)
            new_item.set_root(catalog)
            new_collection.add_item(new_item)

    catalog.make_all_asset_hrefs_relative()

    return catalog


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
            for i in col1_.get_stac_objects(pystac.RelType.ITEM):
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

    if destination:
        # TODO test
        make_links_relative_to_path(destination, catalog_2)
    else:
        destination = dirname(catalog_2.get_self_href())

    # Save the merged catalog
    try:
        print("Validating and saving...")
        catalog_2.validate()
        rmtree(destination) if not destination else None # Remove the old catalog and replace it with the new one
        catalog_2.normalize_and_save(root_href=destination, 
                                     catalog_type=catalog_type
                                     )
        print("Success!")
    except pystac.STACValidationError:
        # Return full callback
        print_exc()
