"""Implements the :stac-ext:`Machine Learning Dataset Extension <ml-dataset>`."""

import traceback
import random

import pystac
from pystac.extensions.base import ExtensionManagementMixin, PropertiesExtension
from pystac.utils import StringEnum
from pystac import STACValidationError
from shutil import rmtree
from os.path import dirname
from pystac.cache import ResolvedObjectCache
from pystac.extensions.hooks import ExtensionHooks
from typing import (Any, 
                    Dict,
                    List, 
                    Tuple, 
                    Generic, 
                    TypeVar,
                    Union, 
                    Set)

T = TypeVar("T", 
            pystac.Item, 
            pystac.Collection, 
            pystac.Catalog)


SCHEMA_URI: str = "https://raw.githubusercontent.com/earthpulse/ml-dataset/main/json-schema/schema.json"
PREFIX: str = "ml-dataset:"


class MLDatasetExtension(
    pystac.Catalog,
    Generic[T],
    PropertiesExtension,
    ExtensionManagementMixin[Union[pystac.Item, pystac.Collection, pystac.Catalog]],
):
    """An abstract class that can be used to extend the properties of a
    :class:`~pystac.Collection`, :class:`~pystac.Item`, or :class:`~pystac.Catalog` with
    properties from the :stac-ext:`Machine Learning Dataset Extension <ml-dataset>`. This class is
    generic over the type of STAC Object to be extended (e.g. :class:`~pystac.Item`,
    :class:`~pystac.Asset`).

    To create a concrete instance of :class:`MLDatasetExtension`, use the
    :meth:`MLDatasetExtension.ext` method. For example:

    .. code-block:: python

       >>> item: pystac.Item = ...
       >>> ml_ext = MLDatasetExtension.ext(item)
    """

    def __init__(self, catalog: pystac.Catalog):
        super().__init__(id=catalog.id, description=catalog.description)
        self.catalog = catalog
        self.id = catalog.id
        self.description = catalog.description
        self.title = catalog.title if catalog.title else None
        self.stac_extensions = catalog.stac_extensions if catalog.stac_extensions else []
        self.extra_fields = self.properties = catalog.extra_fields if catalog.extra_fields else {}
        self.links = catalog.links
        self._resolved_objects = ResolvedObjectCache()
        
    def apply(
        self, name: str = None
    ) -> None:
        self.name = name

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, v: str) -> None:
        self.extra_fields[f'{PREFIX}name'] = v

    @property
    def tasks(self) -> List:
        return self._tasks

    @tasks.setter
    def tasks(self, v: List|Tuple) -> None:
        self.extra_fields[f'{PREFIX}tasks'] = v

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, v: str) -> None:
        self.extra_fields[f'{PREFIX}type'] = v

    @property
    def inputs_type(self) -> str:
        return self._inputs_type

    @inputs_type.setter
    def inputs_type(self, v: str) -> None:
        self.extra_fields[f'{PREFIX}inputs-type'] = v

    @property
    def annotations_type(self) -> str:
        return self._annotations_type

    @annotations_type.setter
    def annotations_type(self, v: str) -> None:
        self.extra_fields[f'{PREFIX}annotations-type'] = v

    @property
    def quality_metrics(self) -> List[dict]:
        return self._quality

    @quality_metrics.setter
    def quality_metrics(self, v: dict) -> None:
        self.extra_fields[f'{PREFIX}quality-metrics'] = v

    @property
    def version(self) -> str:
        return self._version

    @version.setter
    def version(self, v: str) -> None:
        self.extra_fields[f'{PREFIX}version'] = v
    
    @property
    def splits(self) -> List[str]:
        return self._splits

    @splits.setter
    def splits(self, v: str) -> None:
        self.extra_fields[f'{PREFIX}splits'] = v

    @classmethod
    def get_schema_uri(cls) -> str:
        return SCHEMA_URI

    def add_metric(self, metric: dict) -> None:
        """Add a metric to this object's set of metrics.

        Args:
             metric : The metric to add.
        """
        if metric not in self.extra_fields[f'{PREFIX}quality-metrics']:
            self.extra_fields[f'{PREFIX}quality-metrics'].append(metric)

    def add_metrics(self, metrics: List[dict]) -> None:
        """Add a list of metrics to this object's set of metrics.

        Args:
             metrics : The metrics to add.
        """
        for metric in metrics:
            self.add_metric(metric)

    def add_children_to_catalog(self,
                                catalog: pystac.Catalog,
                                items: List[pystac.Item],
                                ) -> None:
        """

        """
        collections = dict()
        for item in items:
            # Get the collection of the item
            collection = item.get_collection()
            if collection.id not in collections:
                collections[collection.id] = pystac.Collection(id=collection.id, 
                                                               description=collection.description, 
                                                               extent=collection.extent)
            collections[collection.id].add_item(item)
        for collection in collections.values():
            # Recalculate the extent of the collection with the new items
            collection_items = [item for item in collection.get_all_items()]
            collection.extent = pystac.Extent.from_items(collection_items)
            catalog.add_child(collection)

    @classmethod
    def ext(cls, obj: T, add_if_missing: bool = False) -> "MLDatasetExtension":
        """Extends the given STAC Object with properties from the 
        :stac-ext:`Machine Learning Dataset Extension <ml-dataset>`.

        This extension can be applied to instances of :class:`~pystac.Catalog`,
        :class:`~pystac.Collection` or :class:`~pystac.Item`.

        Raises:
            pystac.ExtensionTypeError : If an invalid object type is passed.
        """
        if isinstance(obj, pystac.Catalog):
            cls.validate_has_extension(obj, add_if_missing)
            return MLDatasetExtension(obj)
        if isinstance(obj, pystac.Collection):
            cls.validate_has_extension(obj, add_if_missing)
            return CollectionMLDatasetExtension(obj)
        elif isinstance(obj, pystac.Item):
            cls.validate_has_extension(obj, add_if_missing)
            return ItemMLDatasetExtension(obj)
        else:
            raise pystac.ExtensionTypeError(cls._ext_error_message(obj))


class CollectionMLDatasetExtension(MLDatasetExtension[pystac.Collection]):
    """A concrete implementation of :class:`MLDatasetExtension` on an
    :class:`~pystac.Collection` that extends the properties of the Collection to include
    properties defined in the :stac-ext:`Machine Learning Dataset Extension <ml-dataset>`.

    This class should generally not be instantiated directly. Instead, call
    :meth:`MLDatasetExtension.ext` on an :class:`~pystac.Collection` to extend it.
    """

    collection: pystac.Collection
    properties: Dict[str, Any]

    def __init__(self, collection: pystac.Collection):
        self.collection = collection
        self.properties = collection.extra_fields

    def __repr__(self) -> str:
        return "<CollectionMLDatasetExtension Item id={}>".format(self.collection.id)



class ItemMLDatasetExtension(MLDatasetExtension[pystac.Item]):
    """A concrete implementation of :class:`MLDatasetExtension` on an
    :class:`~pystac.Item` that extends the properties of the Item to include properties
    defined in the :stac-ext:`Machine Learning Dataset Extension <ml-dataset>`.

    This class should generally not be instantiated directly. Instead, call
    :meth:`MLDatasetExtension.ext` on an :class:`~pystac.Item` to extend it.
    """

    item: pystac.Item
    properties: Dict[str, Any]

    def __init__(self, item: pystac.Item):
        self.item = item
        self.properties = item.properties

    def __repr__(self) -> str:
        return "<ItemMLDatasetExtension Item id={}>".format(self.item.id)


class MLDatasetExtensionHooks(ExtensionHooks):
    schema_uri: str = SCHEMA_URI
    prev_extension_ids: Set[str] = set()
    stac_object_types = {
        pystac.STACObjectType.CATALOG,
        pystac.STACObjectType.COLLECTION,
        pystac.STACObjectType.ITEM,
    }


STORAGE_EXTENSION_HOOKS: ExtensionHooks = MLDatasetExtensionHooks()


def add_ml_extension(catalog: pystac.Catalog|str, 
                     destination: str = None,  
                     make_splits: bool = False,
                     splits_names: list = ('Training', 'Validation', 'Test'),
                     split_proportions: List[int] = (80, 10, 10),
                     **kwargs) -> None:
    """
    Adds the ML Dataset extension to a STAC catalog.

    Args:
        catalog : The STAC catalog to add the extension to.
        destination : The destination path to save the catalog to.
        splits : The splits to make.
        split_proportions : The proportions of the splits.
    """
    if not isinstance(catalog, pystac.Catalog) and isinstance(catalog, str):
        catalog = pystac.read_file(catalog)
    else:
        raise pystac.ExtensionTypeError(
            f"MLDatasetExtension does not apply to type '{type(catalog).__name__}'"
        )

    catalog_ml_dataset = MLDatasetExtension.ext(catalog, add_if_missing=True)

    # Get all items to generate the new catalog
    # TODO check why is this necessary to not delete items and collections
    items = catalog.get_all_items()

    for i in items:
        pass

    for key, value in kwargs.items():
        setattr(catalog_ml_dataset, key, value)

    # Make splits if requested
    if make_splits:
        catalog_ml_dataset.splits = splits_names
        # train_size, test_size, val_size = split_proportions
        # make_splits(catalog_ml_dataset, 
        #             train_size=train_size, 
        #             test_size=test_size,
        #             val_size=val_size,
        #             **kwargs)
        # # Normalize the ref on the same folder
        # catalog_ml_dataset.normalize_hrefs(root_href=dirname(catalog.get_self_href()))

    try:
        # catalog_ml_dataset.validate()   # TODO validate
        if not destination:
            destination = dirname(catalog.get_self_href())
            rmtree(destination)   # Remove the old catalog and replace it with the new one
        catalog_ml_dataset.save(dest_href=destination)
    except STACValidationError as error:
        # Return full callback
        traceback.print_exc()


def make_splits(catalog: MLDatasetExtension,
                train_size: int,
                test_size: int,
                val_size: int = 0,
                verbose: bool = True,
                **kwargs
                ) -> None:
    """
    Makes the splits of the dataset.

    Args:
        catalog : The STAC catalog to add the extension to.
        train_size : The percentage of the dataset to use for training.
        test_size : The percentage of the dataset to use for testing.
        val_size : The percentage of the dataset to use for validation.
        verbose : Whether to print the sizes of the splits.
    """
    if train_size + test_size + val_size != 100:
        raise ValueError("The sum of the splits must be 100")
    
    items = [item for item in catalog.get_all_items()]

    # Calculate indices to split the items
    length = len(items)
    idx_train = int(train_size/100 * length)
    idx_test = int(test_size/100 * length)
    if val_size:
        idx_val = int(val_size/100 * length)

    print('Generating splits...')
    if verbose:
        print(f"Total size: {length}")
        print(f"Train size: {idx_train}")
        print(f"Test size: {idx_test}")
        if val_size:
            print(f"Validation size: {idx_val}")

    # Make sure the items are shuffled
    random.shuffle(items)

    # Split the items
    train_items = items[:idx_train]
    test_items = items[idx_train:idx_train+idx_test]
    if val_size:
        val_items = items[idx_train+idx_test:idx_train+idx_test+idx_val]

    # Create the subcatalogs
    for split_type, split_data in zip(["Training", "Test", "Validation"], [train_items, test_items, val_items]):
        catalog.create_and_add_split(catalog, split_data, split_type, **kwargs)
        
    # Remove collections from the root catalog
    for collection in catalog.get_children():
        if collection.STAC_OBJECT_TYPE == pystac.STACObjectType.COLLECTION:
            catalog.remove_child(collection.id)

    print('Success!')