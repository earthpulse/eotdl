'''
Paths utils
'''

from os.path import dirname
from typing import Union, Optional
from glob import glob


def count_ocurrences(text: str, text_list: list) -> int:
    """
    Count the number of ocurrences of a string in a list of strings

    :param text: string to count the ocurrences
    """
    count = 0
    for string in text_list:
        if text in string:
            count += 1
    return count


def cut_images(images_list: Union[list, tuple]) -> list:
    """
    Get the directory name of each image and return a list of unique directories

    :param images_list: list of images

    :return: list of unique directories
    """
    dirnames = list()
    images = list()

    for image in images_list:
        dir = dirname(image)
        if dir not in dirnames:
            dirnames.append(dir)
            images.append(image)

    return images


def get_all_images_in_path(path: str, image_format: Optional[str] = 'tif') -> list:
        """
        Get all the images in a directory

        :param path: path to the directory

        :return: list of images
        """
        return glob(str(path) + f'/**/*.{image_format}', recursive=True)
