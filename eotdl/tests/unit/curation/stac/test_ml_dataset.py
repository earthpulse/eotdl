import os
import pytest

from eotdl.curation.stac.extensions import add_ml_extension, MLDatasetQualityMetrics
from eotdl.curation.stac.extensions.ml_dataset import MLDatasetExtension

from .fixtures import tmp_stac_catalog, tmp_stac_catalog_labels


def test_add_ml_extension(tmp_stac_catalog):
    add_ml_extension(tmp_stac_catalog)

    assert MLDatasetExtension.has_extension(tmp_stac_catalog) is True


def test_add_ml_extension_export(tmp_stac_catalog):
    add_ml_extension(tmp_stac_catalog, destination="tmp/exported_catalog")

    assert os.path.exists("tmp/exported_catalog/catalog.json")


def test_add_ml_extension_parameters(tmp_stac_catalog):
    add_ml_extension(
        tmp_stac_catalog,
        name="Q2 Dataset",
        tasks=["segmentation"],
        inputs_type=["satellite imagery"],
        annotations_type="raster",
        version="0.1.0",
    )

    assert tmp_stac_catalog.extra_fields["ml-dataset:name"] == "Q2 Dataset"
    assert tmp_stac_catalog.extra_fields["ml-dataset:tasks"] == ["segmentation"]
    assert tmp_stac_catalog.extra_fields["ml-dataset:inputs-type"] == [
        "satellite imagery"
    ]
    assert tmp_stac_catalog.extra_fields["ml-dataset:annotations-type"] == "raster"
    assert tmp_stac_catalog.extra_fields["ml-dataset:version"] == "0.1.0"


def test_add_ml_extension_splits_without_labels(tmp_stac_catalog):
    with pytest.raises(AttributeError):
        add_ml_extension(
            tmp_stac_catalog,
            splits=True,
            splits_collection_id="labels",
            name="Q2 Dataset",
            tasks=["segmentation"],
            inputs_type=["satellite imagery"],
            annotations_type="raster",
            version="0.1.0",
        )


def test_add_ml_extension_splits(tmp_stac_catalog_labels):
    add_ml_extension(
        tmp_stac_catalog_labels,
        splits=True,
        splits_collection_id="labels",
        name="Q2 Dataset",
        tasks=["segmentation"],
        inputs_type=["satellite imagery"],
        annotations_type="raster",
        version="0.1.0",
    )

    assert tmp_stac_catalog_labels.extra_fields["ml-dataset:splits"] == (
        "Training",
        "Validation",
        "Test",
    )

    collection = tmp_stac_catalog_labels.get_child("labels")
    assert "ml-dataset:split-items" in collection.extra_fields


def test_add_ml_extension_quality_metrics(tmp_stac_catalog_labels):
    add_ml_extension(
        tmp_stac_catalog_labels,
        splits=True,
        splits_collection_id="labels",
        name="Q2 Dataset",
        tasks=["segmentation"],
        inputs_type=["satellite imagery"],
        annotations_type="raster",
        version="0.1.0",
    )

    MLDatasetQualityMetrics.calculate(tmp_stac_catalog_labels)

    assert "ml-dataset:quality-metrics" in tmp_stac_catalog_labels.extra_fields
    quality_metrics = tmp_stac_catalog_labels.extra_fields["ml-dataset:quality-metrics"]
    assert isinstance(quality_metrics, list) is True
    assert len(quality_metrics) == 2
    assert quality_metrics[0]["name"] == "spatial-duplicates"
    assert quality_metrics[1]["name"] == "classes-balance"
