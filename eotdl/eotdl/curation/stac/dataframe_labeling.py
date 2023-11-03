"""
Module for the labeling strategy when creating a STAC catalog from a dataframe
"""

from os.path import basename


class LabelingStrategy:
    """
    Labeling strategy interface to be implemented by concrete labeling strategies
    """

    def get_images_labels(self, images):
        """
        Get the labels of the images
        """
        return


class UnlabeledStrategy(LabelingStrategy):
    """
    Assumes the images are not labeled, and returns the entire filename as label
    """

    def __init__(self):
        super().__init__()

    def get_images_labels(self, images):
        """
        Get the labels of the images
        """
        labels = []
        for image in images:
            labels.append(basename(image).split(".")[0])
        ixs = [labels.index(x) for x in labels]

        return labels, ixs


class LabeledStrategy(LabelingStrategy):
    """
    Assumes the images are already labeled, and returns the labels.
    The images filenames must follow the pattern: <label>_<id>.<ext>
    """

    def __init__(self):
        super().__init__()

    def get_images_labels(self, images):
        """
        Get the labels of the images
        """
        labels = []
        for image in images:
            image_basename = basename(image).split(".")[
                0
            ]  # Get filename without extension
            label = image_basename.split("_")[0]
            labels.append(label)

        ixs = [labels.index(x) for x in labels]

        return labels, ixs
