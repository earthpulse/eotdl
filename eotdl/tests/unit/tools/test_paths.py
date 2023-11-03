from eotdl.tools import count_ocurrences, cut_images, get_all_images_in_path


# Test for count_ocurrences function
def test_count_ocurrences():
    test_list = ["apple", "orange", "applejuice", "applepie", "banana"]
    assert count_ocurrences("apple", test_list) == 3
    assert count_ocurrences("orange", test_list) == 1
    assert count_ocurrences("mango", test_list) == 0


# Test for cut_images function
def test_cut_images():
    test_images_list = [
        "/path/to/dir1/image1.tif",
        "/path/to/dir1/image2.tif",
        "/path/to/dir2/image1.tif",
        "/path/to/dir3/image1.tif"
    ]
    cut_list = cut_images(test_images_list)
    assert len(cut_list) == 3
    assert "/path/to/dir1/image1.tif" in cut_list
    assert "/path/to/dir2/image1.tif" in cut_list
    assert "/path/to/dir3/image1.tif" in cut_list


# Test for get_all_images_in_path using pytest's tmpdir fixture
def test_get_all_images_in_path(tmpdir):
    # Create dummy image files in tmpdir
    sub_dir = tmpdir.mkdir("sub")
    sub_dir.join("image1.tif").write("content")
    sub_dir.join("image2.tif").write("content")
    tmpdir.join("image3.tif").write("content")

    # Get all tif images in tmpdir
    images = get_all_images_in_path(str(tmpdir))
    assert len(images) == 3
    assert any("image1.tif" in path for path in images)
    assert any("image2.tif" in path for path in images)
    assert any("image3.tif" in path for path in images)
