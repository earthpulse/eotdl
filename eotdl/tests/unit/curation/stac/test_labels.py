import os
import pystac

from eotdl.curation.stac.extensions import ScaneoLabeler, ImageNameLabeler

scaneo_labeler = ScaneoLabeler()
image_labeler = ImageNameLabeler()


from .fixtures import tmp_stac_catalog, tmp_stac_catalog_labels, EXAMPLE_DATA_DIR


def test_scaneo_labeler(tmp_stac_catalog):
    from pystac.extensions.label import LabelExtension

    labels_extra_properties = {'label_methods': ["manual"]}
    scaneo_labeler.generate_stac_labels(
        catalog=tmp_stac_catalog,
        root_folder=os.path.join(EXAMPLE_DATA_DIR, 'labels_scaneo'),
        collection='sentinel-2-l2a',
        **labels_extra_properties
    )

    assert tmp_stac_catalog.get_child('labels')
    labels_collection = tmp_stac_catalog.get_child('labels')
    assert LabelExtension.has_extension(labels_collection)
    summaries = labels_collection.summaries.to_dict()
    assert summaries['label:classes']
    assert summaries['label:type'] == 'vector'
    assert summaries['label:methods'] == ["manual"]
