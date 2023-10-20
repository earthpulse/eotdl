'''
Module for the labeling strategy when creating a STAC catalog from a dataframe
'''

import pystac
from os.path import basename


class LabelingStrategy:
    """
    Labeling strategy interface to be implemented by concrete labeling strategies
    """

    def __init__(self):
        pass

    def get_images_labels(self, images):
        pass


class UnlabeledStrategy(LabelingStrategy):
    """
    Assumes the images are not labeled, and returns the entire filename as label
    """

    def __init__(self):
        super().__init__()

    def get_images_labels(self, images):
        """
        """
        labels = list()
        for image in images:
            labels.append(basename(image).split('.')[0])
        ixs = [labels.index(x) for x in labels]

        return labels, ixs


class LabeledStrategy(LabelingStrategy):
    """
    Assumes the images are already labeled, and returns the labels.
    The images filenames must follow the pattern: <label>_<id>.<ext> or <label>-<id>.<ext>
    """

    def __init__(self):
        super().__init__()

    def get_images_labels(self, images):
        """
        """
        labels = list()
        for image in images:
            image_basename = basename(image).split('.')[0]   # Get filename without extension
            if '_' in image_basename:
                separator = '_'
            elif '-' in image_basename:
                separator = '-'
            try:
                # Ensure the image has format <label>_<number> or <label>-<number>
                int(image_basename.split(separator)[1])
                label = image_basename.split(separator)[0]
            except ValueError:
                label = image_basename
            labels.append(label)

        ixs = [labels.index(x) for x in labels]

        return labels, ixs
