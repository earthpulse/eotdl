"""Implements the :stac-ext:`Machine Learning Dataset Extension <ml-dataset>`."""

from typing import Any, Dict, List, Optional, Generic, TypeVar, Union, Set
from shutil import rmtree
from os.path import dirname, exists

import traceback
import json
import random

import pystac

from tqdm import tqdm
from pystac.extensions.base import ExtensionManagementMixin, PropertiesExtension
from pystac.extensions.label import LabelExtension
from pystac import STACValidationError
from pystac.cache import ResolvedObjectCache
from pystac.extensions.hooks import ExtensionHooks
from ....tools import make_links_relative_to_path

T = TypeVar("T", pystac.Item, pystac.Collection, pystac.Catalog)


SCHEMA_URI: str = "https://raw.githubusercontent.com/earthpulse/ml-dataset/main/json-schema/schema.json"
PREFIX: str = "ml-dataset:"


class MLDatasetExtension(
    pystac.Catalog,
    Generic[T],
    PropertiesExtension,
    ExtensionManagementMixin[
        Union[pystac.item.Item, pystac.collection.Collection, pystac.catalog.Catalog]
    ],
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

    catalog: pystac.Catalog
    """The :class:`~pystac.Catalog` being extended."""

    properties: Dict[str, Any]
    """The :class:`~pystac.Catalog` extra fields, including extension properties."""

    links: List[pystac.Link]
    """The list of :class:`~pystac.Link` objects associated with the
    :class:`~pystac.Catalog` being extended, including links added by this extension.
    """

    def __init__(self, catalog: pystac.Catalog):
        super().__init__(id=catalog.id, description=catalog.description)
        self._catalog = catalog
        self.id = catalog.id
        self.description = catalog.description
        self.title = catalog.title if catalog.title else None
        self.stac_extensions = (
            catalog.stac_extensions if catalog.stac_extensions else []
        )
        self.extra_fields = self.properties = (
            catalog.extra_fields if catalog.extra_fields else {}
        )
        self.links = catalog.links
        self._resolved_objects = ResolvedObjectCache()

    def apply(self, name: str = None) -> None:
        """
        Applies the :stac-ext:`Machine Learning Dataset Extension <ml-dataset>` to the extended
        :class:`~pystac.Catalog`.
        """
        self.name = name

    @property
    def name(self) -> str:
        """
        Name of the ML Dataset.
        """
        return self.extra_fields[f"{PREFIX}name"]

    @name.setter
    def name(self, v: str) -> None:
        """
        Set the name of the ML Dataset.
        """
        self.extra_fields[f"{PREFIX}name"] = v

    @property
    def tasks(self) -> List:
        """
        Tasks of the ML Dataset.
        """
        return self.extra_fields[f"{PREFIX}tasks"]

    @tasks.setter
    def tasks(self, v: Union[list, tuple]) -> None:
        """
        Set the tasks of the ML Dataset.
        """
        self.extra_fields[f"{PREFIX}tasks"] = v

    @property
    def type(self) -> str:
        """
        Type of the ML Dataset.
        """
        return self.extra_fields[f"{PREFIX}type"]

    @type.setter
    def type(self, v: str) -> None:
        """
        Set the type of the ML Dataset.
        """
        self.extra_fields[f"{PREFIX}type"] = v

    @property
    def inputs_type(self) -> str:
        """
        Inputs type of the ML Dataset.
        """
        return self.extra_fields[f"{PREFIX}inputs-type"]

    @inputs_type.setter
    def inputs_type(self, v: str) -> None:
        """
        Set the inputs type of the ML Dataset.
        """
        self.extra_fields[f"{PREFIX}inputs-type"] = v

    @property
    def annotations_type(self) -> str:
        """
        Annotations type of the ML Dataset.
        """
        return self.extra_fields[f"{PREFIX}annotations-type"]

    @annotations_type.setter
    def annotations_type(self, v: str) -> None:
        """
        Set the annotations type of the ML Dataset.
        """
        self.extra_fields[f"{PREFIX}annotations-type"] = v

    @property
    def splits(self) -> List[str]:
        """
        Splits of the ML Dataset.
        """
        return self.extra_fields[f"{PREFIX}splits"]

    @splits.setter
    def splits(self, v: dict) -> None:
        """
        Set the splits of the ML Dataset.
        """
        self.extra_fields[f"{PREFIX}splits"] = v

    @property
    def quality_metrics(self) -> List[dict]:
        """
        Quality metrics of the ML Dataset.
        """
        return self.extra_fields[f"{PREFIX}quality-metrics"]

    @quality_metrics.setter
    def quality_metrics(self, v: dict) -> None:
        """
        Set the quality metrics of the ML Dataset.
        """
        self.extra_fields[f"{PREFIX}quality-metrics"] = v

    @property
    def version(self) -> str:
        """
        Version of the ML Dataset.
        """
        return self.extra_fields[f"{PREFIX}version"]

    @version.setter
    def version(self, v: str) -> None:
        """
        Set the version of the ML Dataset.
        """
        self.extra_fields[f"{PREFIX}version"] = v

    @classmethod
    def get_schema_uri(cls) -> str:
        """
        Get the JSON Schema URI that validates the extended object.
        """
        return SCHEMA_URI

    def add_metric(self, metric: dict) -> None:
        """Add a metric to this object's set of metrics.

        Args:
             metric : The metric to add.
        """
        if not self.extra_fields.get(f"{PREFIX}quality-metrics"):
            self.extra_fields[f"{PREFIX}quality-metrics"] = []

        if metric not in self.extra_fields[f"{PREFIX}quality-metrics"]:
            self.extra_fields[f"{PREFIX}quality-metrics"].append(metric)

    def add_metrics(self, metrics: List[dict]) -> None:
        """Add a list of metrics to this object's set of metrics.

        Args:
             metrics : The metrics to add.
        """
        for metric in metrics:
            self.add_metric(metric)

    @classmethod
    def ext(cls, obj: T, add_if_missing: bool = False):
        """Extends the given STAC Object with properties from the
        :stac-ext:`Machine Learning Dataset Extension <ml-dataset>`.

        This extension can be applied to instances of :class:`~pystac.Catalog`,
        :class:`~pystac.Collection` or :class:`~pystac.Item`.

        Raises:
            pystac.ExtensionTypeError : If an invalid object type is passed.
        """
        if isinstance(obj, pystac.Collection):
            cls.validate_has_extension(obj, add_if_missing)
            return CollectionMLDatasetExtension(obj)
        elif isinstance(obj, pystac.Catalog):
            cls.validate_has_extension(obj, add_if_missing)
            return MLDatasetExtension(obj)
        elif isinstance(obj, pystac.Item):
            cls.validate_has_extension(obj, add_if_missing)
            return ItemMLDatasetExtension(obj)
        else:
            raise pystac.ExtensionTypeError(cls._ext_error_message(obj))


class CollectionMLDatasetExtension(MLDatasetExtension[pystac.Collection]):
    """A concrete implementation of :class:`MLDatasetExtension` on an
    :class:`~pystac.Collection` that extends the properties of the Collection to include
    properties defined in the :stac-ext:`Machine Learning Dataset Extension <ml-dataset>`.
    """

    collection: pystac.Collection
    properties: Dict[str, Any]

    def __init__(self, collection: pystac.Collection):
        self.collection = collection
        self.properties = collection.extra_fields
        self.properties[f"{PREFIX}split-items"] = []

    def __repr__(self) -> str:
        return f"<CollectionMLDatasetExtension Item id={self.collection.id}>"

    @property
    def splits(self) -> List[dict]:
        """
        Splits of the ML Dataset.
        """
        return self.extra_fields[f"{PREFIX}splits"]

    @splits.setter
    def splits(self, v: dict) -> None:
        """
        Set the splits of the ML Dataset.
        """
        self.properties[f"{PREFIX}split-items"] = v

    def add_split(self, v: dict) -> None:
        """
        Add a split to the ML Dataset.
        """
        self.properties[f"{PREFIX}split-items"].append(v)

    def create_and_add_split(
        self, split_data: List[pystac.Item], split_type: str
    ) -> None:
        """
        Create and add a split to the ML Dataset.
        """
        items_ids = [item.id for item in split_data]
        items_ids.sort()

        split = {"name": split_type, "items": items_ids}

        if not self.properties.get(f"{PREFIX}split-items"):
            self.properties[f"{PREFIX}split-items"] = []

        self.add_split(split)
        print(f"Generating {split_type} split...")
        for _item in tqdm(split_data):
            item = self.collection.get_item(_item.id)
            if item:
                item_ml = MLDatasetExtension.ext(item, add_if_missing=True)
                item_ml.split = split_type


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

    @property
    def split(self) -> str:
        """
        Split of the ML Dataset.
        """
        return self.properties[f"{PREFIX}split"]

    @split.setter
    def split(self, v: str) -> None:
        """
        Set the split of the ML Dataset.
        """
        self.properties[f"{PREFIX}split"] = v

    def __repr__(self) -> str:
        return f"<ItemMLDatasetExtension Item id={self.item.id}>"


class MLDatasetQualityMetrics:
    """
    ML Dataset Quality Metrics
    """

    @classmethod
    def calculate(cls, catalog: Union[pystac.Catalog, str]) -> None:
        """
        Calculate the quality metrics of the catalog
        """
        if isinstance(catalog, str):
            catalog = MLDatasetExtension(pystac.read_file(catalog))
        elif isinstance(catalog, pystac.Catalog):
            catalog = MLDatasetExtension(catalog)
        # Check the catalog has the extension
        if not MLDatasetExtension.has_extension(catalog):
            raise pystac.ExtensionNotImplemented(
                f"MLDatasetExtension does not apply to type '{type(catalog).__name__}'"
            )

        try:
            catalog.add_metric(cls._search_spatial_duplicates(catalog))
            catalog.add_metric(cls._get_classes_balance(catalog))
        except AttributeError as exc:
            raise pystac.ExtensionNotImplemented(
                f"The catalog does not have the required properties or the ML-Dataset extension to calculate the metrics: {exc}"
            )
        finally:
            catalog.make_all_asset_hrefs_relative()

        try:
            print("Validating and saving...")
            catalog.validate()
            destination = dirname(catalog.get_self_href())
            rmtree(
                destination
            )  # Remove the old catalog and replace it with the new one
            catalog.set_root(catalog)
            catalog.normalize_and_save(root_href=destination)
            print("Success!")
        except STACValidationError:
            # Return full callback
            traceback.print_exc()

    @staticmethod
    def _search_spatial_duplicates(catalog: pystac.Catalog):
        """
        Search for spatial duplicates in the catalog
        """
        items = list(
            set(
                [
                    item
                    for item in tqdm(
                        catalog.get_items(recursive=True),
                        desc="Looking for spatial duplicates...",
                    )
                    if not LabelExtension.has_extension(item)
                ]
            )
        )

        # Initialize the spatial duplicates dict
        spatial_duplicates = {"name": "spatial-duplicates", "values": [], "total": 0}

        items_bboxes = {}
        for item in items:
            # Get the item bounding box
            bbox = str(item.bbox)
            # If the bounding box is not in the items dict, add it
            if bbox not in items_bboxes.keys():
                items_bboxes[bbox] = item.id
            # If the bounding box is already in the items dict, add it to the duplicates dict
            else:
                spatial_duplicates["values"].append(
                    {"item": item.id, "duplicate": items_bboxes[bbox]}
                )
                spatial_duplicates["total"] += 1

        return spatial_duplicates

    @staticmethod
    def _get_classes_balance(catalog: pystac.Catalog) -> dict:
        """
        Get the classes balance of the catalog
        """

        def get_label_properties(items: List[pystac.Item]) -> List:
            """
            Get the label properties of the catalog
            """
            label_properties = []
            for label in items:
                label_ext = LabelExtension.ext(label)
                for prop in label_ext.label_properties:
                    if prop not in label_properties:
                        label_properties.append(prop)

            return label_properties

        catalog.make_all_asset_hrefs_absolute()

        labels = list(
            set(
                [
                    item
                    for item in tqdm(
                        catalog.get_items(recursive=True),
                        desc="Calculating classes balance...",
                    )
                    if LabelExtension.has_extension(item)
                ]
            )
        )

        # Initialize the classes balance dict
        classes_balance = {"name": "classes-balance", "values": []}
        label_properties = get_label_properties(labels)

        for prop in label_properties:
            property_balance = {"name": prop, "values": []}
            properties = {}
            for label in labels:
                if 'labels' not in label.assets:
                    continue
                asset_path = label.assets["labels"].href
                # Open the linked geoJSON to obtain the label properties
                try:
                    with open(asset_path, mode="r", encoding="utf-8") as f:
                        label_data = json.load(f)
                except FileNotFoundError:
                    raise FileNotFoundError(
                        f"The file {asset_path} does not exist. Make sure the assets hrefs are correct"
                    )
                # Get the property
                for feature in label_data["features"]:
                    if prop in feature["properties"]:
                        property_value = feature["properties"][prop]
                    else:
                        if feature["properties"]["labels"]:
                            property_value = feature["properties"]["labels"][0]
                        else:
                            continue
                    if property_value not in properties:
                        properties[property_value] = 0
                    properties[property_value] += 1

            # Create the property balance dict
            total_labels = sum(properties.values())
            for key, value in properties.items():
                property_balance["values"].append(
                    {
                        "class": key,
                        "total": value,
                        "percentage": int(value / total_labels * 100),
                    }
                )

            classes_balance["values"].append(property_balance)

        catalog.make_all_asset_hrefs_relative()

        return classes_balance


class MLDatasetExtensionHooks(ExtensionHooks):
    """
    ML Dataset Extension Hooks
    """
    schema_uri: str = SCHEMA_URI
    prev_extension_ids: Set[str] = set()
    stac_object_types = {
        pystac.STACObjectType.CATALOG,
        pystac.STACObjectType.COLLECTION,
        pystac.STACObjectType.ITEM,
    }


STORAGE_EXTENSION_HOOKS: ExtensionHooks = MLDatasetExtensionHooks()


def add_ml_extension(
    catalog: Union[pystac.Catalog, str],
    destination: Optional[str] = None,
    splits: Optional[bool] = False,
    splits_collection_id: Optional[str] = "labels",
    splits_names: Optional[list] = ("Training", "Validation", "Test"),
    split_proportions: Optional[List[int]] = (80, 10, 10),
    catalog_type: Optional[pystac.CatalogType] = pystac.CatalogType.SELF_CONTAINED,
    **kwargs,
) -> None:
    """
    Adds the ML Dataset extension to a STAC catalog.
    """
    if not isinstance(catalog, pystac.Catalog) and isinstance(catalog, str):
        catalog = pystac.read_file(catalog)
    elif isinstance(catalog, pystac.Catalog):
        pass
    else:
        raise pystac.ExtensionTypeError(
            f"MLDatasetExtension does not apply to type '{type(catalog).__name__}'"
        )

    catalog_ml_dataset = MLDatasetExtension.ext(catalog, add_if_missing=True)
    if destination:
        catalog_ml_dataset.set_self_href(destination + "/catalog.json")
    else:
        destination = dirname(catalog.get_self_href())
    catalog_ml_dataset.set_root(catalog_ml_dataset)

    # Set extension properties
    for key, value in kwargs.items():
        setattr(catalog_ml_dataset, key, value)

    # Make splits if needed
    if splits:
        catalog_ml_dataset.splits = splits_names  # Add the splits names to the catalog
        train_size, test_size, val_size = split_proportions
        splits_collection = catalog.get_child(
            splits_collection_id
        )  # Get the collection to split
        if not splits_collection:
            raise AttributeError(
                f"The catalog does not have a collection with the id {splits_collection_id}"
            )
        make_splits(
            splits_collection,
            train_size=train_size,
            test_size=test_size,
            val_size=val_size,
            **kwargs,
        )

    # Normalize the ref on the same folder
    if destination:
        catalog_ml_dataset = make_links_relative_to_path(
            destination, catalog_ml_dataset
        )

    try:
        print("Validating and saving...")
        catalog_ml_dataset.validate()
        rmtree(destination) if exists(
            destination
        ) else None  # Remove the old catalog and replace it with the new one
        catalog_ml_dataset.normalize_and_save(
            root_href=destination, catalog_type=catalog_type
        )
        print("Success!")
    except STACValidationError:
        # Return full callback
        traceback.print_exc()


def make_splits(
    labels_collection: Union[CollectionMLDatasetExtension, pystac.Collection, str],
    splits_names: Optional[List[str]] = ("Training", "Validation", "Test"),
    splits_proportions: Optional[List[int]] = (80, 10, 10),
    verbose: Optional[bool] = True,
    **kwargs: Optional[dict],
) -> None:
    """
    Makes the splits of the labels collection.
    """
    if isinstance(labels_collection, str):
        labels_collection = pystac.read_file(labels_collection)

    train_size, test_size, val_size = splits_proportions

    if train_size + test_size + val_size != 100:
        raise ValueError("The sum of the splits must be 100")

    # Get all items in the labels collection
    items = list(labels_collection.get_items(recursive=True))

    # Calculate indices to split the items
    length = len(items)
    idx_train = int(train_size / 100 * length)
    idx_test = int(test_size / 100 * length)
    if val_size:
        idx_val = int(val_size / 100 * length)

    print("Generating splits...")
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
    test_items = items[idx_train: idx_train + idx_test]
    if val_size:
        val_items = items[idx_train + idx_test: idx_train + idx_test + idx_val]

    # Create the splits in the collection
    labels_collection = MLDatasetExtension.ext(labels_collection, add_if_missing=True)
    for split_type, split_data in zip(
        splits_names, [train_items, test_items, val_items]
    ):
        labels_collection.create_and_add_split(split_data, split_type)

    print("Success on splits generation!")
