"""Implements the :stac-ext:`Machine Learning Dataset Extension <ml-dataset>`."""

import traceback
import random

import pystac
from pystac.extensions.base import ExtensionManagementMixin
from pystac import STACValidationError
from shutil import rmtree
from os.path import dirname
from pystac.cache import ResolvedObjectCache

from typing import Any, Dict, List, Tuple


SCHEMA_URI: str = "https://raw.githubusercontent.com/earthpulse/ml-dataset/main/json-schema/schema.json"
PREFIX: str = "ml-dataset:"


class MLDatasetExtension(
    pystac.Catalog, ExtensionManagementMixin[pystac.Catalog]
):
    
    catalog: pystac.Catalog
    """The :class:`~pystac.Catalog` being extended."""

    properties: Dict[str, Any]
    """The :class:`~pystac.Catalog` extra fields, including extension properties."""

    links: List[pystac.Link]
    """The list of :class:`~pystac.Link` objects associated with the
    :class:`~pystac.Catalog` being extended, including links added by this extension.
    """

    splits: List[pystac.Link]
    """The list of :class:`~pystac.Link` objects associated with the root
    :class:`~pystac.Catalog` representing the splits of the dataset.
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
        self.splits = []
        self.quality_metrics = []
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
    def splits(self) -> List[pystac.Link]:
        return self._splits

    @splits.setter
    def splits(self, v: str) -> None:
        self.extra_fields[f'{PREFIX}splits'] = v

    @classmethod
    def get_schema_uri(cls) -> str:
        return SCHEMA_URI
    
    def add_split(self, split: pystac.Link) -> None:
        """Add a split to this object's set of splits.

        Args:
             split : The split to add.
        """
        split.set_owner(self)
        split_js = split.to_dict()
        if split_js not in self.extra_fields[f'{PREFIX}splits']:
            self.extra_fields[f'{PREFIX}splits'].append(split_js)

    def add_splits(self, splits: List[pystac.Link]) -> None:
        """Add a list of splits to this object's set of splits.

        Args:
             splits : The splits to add.
        """
        for split in splits:
            self.add_split(split)

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

    def create_and_add_split(self,
                                  catalog: pystac.Catalog,
                                  items: List[pystac.Item],
                                  split: str,
                                  **kwargs) -> None:
        """
        """
        split_catalog = self.ext(pystac.Catalog(id=f'{catalog.id}-{split.lower()}', description=f"{split} split"), add_if_missing=True)
        for key, value in kwargs.items():
            setattr(split_catalog, key, value)
        split_catalog.type = split
        catalog.add_children_to_catalog(split_catalog, items)
        catalog.add_child(split_catalog)

        split = pystac.Link(
            rel=pystac.RelType.CHILD,
            target=split_catalog.get_self_href(),
            media_type=pystac.MediaType.JSON,
            title=split,
        )
        self.add_split(split)

    def add_children_to_catalog(self,
                                catalog: pystac.Catalog,
                                items: List[pystac.Item],
                                ) -> None:
        """

        """
        # TODO recalculate collection extent
        collections = dict()
        for item in items:
            # Get the collection of the item
            collection = item.get_collection()
            if collection.id not in collections:
                collections[collection.id] = pystac.Collection(id=collection.id, 
                                                               description=collection.description, 
                                                               extent=collection.extent)
            collections[collection.id].add_item(item)
            # TODO items path should be the same as before
        for collection in collections.values():
            catalog.add_child(collection)

    @classmethod
    def ext(cls, obj: pystac.Catalog, add_if_missing: bool = False) -> "MLDatasetExtension":
        if isinstance(obj, pystac.Catalog):
            cls.validate_has_extension(obj, add_if_missing)
            return MLDatasetExtension(obj)
        else:
            raise pystac.ExtensionTypeError(
                f"MLDatasetExtension does not apply to type '{type(obj).__name__}'"
            )


def add_ml_extension(catalog: pystac.Catalog, 
                     destination: str = None,  
                     splits: bool = False,
                     split_proportions: List[int] = (80, 10, 10),
                     **kwargs) -> None:
    """
    Adds the ML Dataset extension to a STAC catalog.

    Args:
        catalog : The STAC catalog to add the extension to.
        destination : The destination path to save the catalog to.

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
    if splits:
        train_size, test_size, val_size = split_proportions
        make_splits(catalog_ml_dataset, 
                    train_size=train_size, 
                    test_size=test_size,
                    val_size=val_size,
                    **kwargs)
        # Normalize the ref on the same folder
        catalog_ml_dataset.normalize_hrefs(root_href=dirname(catalog.get_self_href()))

    try:
        catalog_ml_dataset.validate()
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
