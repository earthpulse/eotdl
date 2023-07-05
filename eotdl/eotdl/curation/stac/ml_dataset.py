"""Implements the :stac-ext:`Machine Learning Dataset Extension <ml-dataset>`."""

import traceback

import pystac
from pystac.extensions.base import ExtensionManagementMixin
from pystac import STACValidationError
from shutil import rmtree
from os.path import dirname

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
        self.catalog = catalog
        self.id = catalog.id
        self.description = catalog.description
        self.title = catalog.title if catalog.title else None
        self.stac_extensions = catalog.stac_extensions if catalog.stac_extensions else []
        self.extra_fields = self.properties = catalog.extra_fields if catalog.extra_fields else {}
        self.links = catalog.links
        self.splits = []
        self.quality_metrics = []
        
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

    @classmethod
    def ext(cls, obj: pystac.Catalog, add_if_missing: bool = False) -> "MLDatasetExtension":
        if isinstance(obj, pystac.Catalog):
            cls.validate_has_extension(obj, add_if_missing)
            return MLDatasetExtension(obj)
        else:
            raise pystac.ExtensionTypeError(
                f"MLDatasetExtension does not apply to type '{type(obj).__name__}'"
            )


def add_ml_extension(catalog: pystac.Catalog, destination: str = None, **kwargs) -> None:
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

    try:
        catalog_ml_dataset.validate()
        if not destination:
            destination = dirname(catalog.get_self_href())
            rmtree(destination)   # Remove the old catalog and replace it with the new one
        catalog_ml_dataset.save(dest_href=destination)
    except STACValidationError as error:
        # Return full callback
        traceback.print_exc()
