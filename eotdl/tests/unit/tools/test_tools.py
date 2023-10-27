from eotdl.tools.tools import *


def test_extract_image_id_in_folder():
    assert extract_image_id_in_folder("path/to/image/20210101T000000.tif", 3) == "20210101T000000.tif"
    assert extract_image_id_in_folder("path/to/image/20210101T000000.tif", 2) == "image"
