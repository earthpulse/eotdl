'''
Module for STAC parsers
'''

from os.path import dirname, basename


class STACIdParser:
    
    def get_item_id(self, raster_path: str):
        """
        Get the ID of the STAC Item from the given raster path

        :param raster_path: path to the raster file
        """
        pass


class StructuredParser(STACIdParser):

    def __init__(self) -> None:
        super().__init__()
    
    def get_item_id(self, raster_path: str):
        """
        Get the ID of the STAC Item from the given raster path.
        This function assumes that the project given by the user is structured,
        meaning that the raster files are stored in a folder with the same name

        :param raster_path: path to the raster file
        """
        tiff_dir_path = dirname(raster_path)
        id = tiff_dir_path.split('/')[-1]

        return id


class UnestructuredParser(STACIdParser):

    def __init__(self) -> None:
        super().__init__()
    
    def get_item_id(self, raster_path: str):
        """
        Get the ID of the STAC Item from the given raster path.
        This function assumes that the project given by the user is unstructured,
        meaning that the raster files are stored in the root folder or in a folder

        :param raster_path: path to the raster file
        """
        id = basename(raster_path).split('.')[0]

        return id
