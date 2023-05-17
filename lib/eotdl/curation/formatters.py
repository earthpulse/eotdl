"""
Module for formatter classes
"""

import rasterio

from os.path import join, exists
from os import listdir, mkdir
from glob import glob
from shutil import rmtree, copyfile
from .metadata import generate_raster_metadata


class Formatter:
    pass


class SHBandsFormatter(Formatter):
    """
    Class for extracting the bands of Sentinel images
    downloaded from Sentinel Hub Services as independent
    images
    """

    def __init__(self):
        super().__init__()

    def extract_sentinel_1_bands(self, 
                                 raster_path: str, 
                                 output_folder: str
                                 ) -> None:
        """
        Extract the bands of a Sentinel-1 image into a desired output
        folder
        
        :param raster: Sentinel-1 image to extract the bands from
        :param output_folder: output folder to write the bands to
        """
        with rasterio.open(raster_path) as raster:
            vh = raster.read(1)
            vv = raster.read(2)

            vh_info = vh, join(output_folder, f'VH.tiff')
            vv_info = vv, join(output_folder, f'VV.tiff')

            # Copy the metadata
            metadata = raster.meta.copy()
            metadata.update({"count": 1})

            for info in vh_info, vv_info:
                band, ds_out = info[0], info[1]
                with rasterio.open(ds_out, "w", **metadata) as dest:
                    dest.write(band, 1)

    def extract_sentinel_2_bands(self, 
                                 raster_path: str, 
                                 output_folder: str
                                 ) -> None:
        """
        Extract the bands of a Sentinel-2 image into a desired output
        folder
        
        :param raster: Sentinel-2 image to extract the bands from
        :param output_folder: output folder to write the bands to
        """
        with rasterio.open(raster_path) as raster:
            for band in range(1, raster.count + 1):   # the +1 allows the writing of the last band
                single_band = raster.read(band)

                if band > 9:   # There is no band 10 but 11 and 12
                    band += 1
                band_n = str(band)
                if len(band_n) == 1:   # Format the band number to 2 digits
                    band_n = f'0{band_n}'
                band_name = f'B{str(band_n)}.tiff'
                ds_out = join(output_folder, band_name)

                # Copy the metadata
                metadata = raster.meta.copy()
                metadata.update({"count": 1})

                with rasterio.open(ds_out, "w", **metadata) as dest:
                    dest.write(single_band, 1)


bands_formatter = SHBandsFormatter()


class SHFolderFormatter(Formatter):
    """
    Class for formatting the directories of Sentinel images downloaded from Sentinel Hub Services
    """

    def __init__(self, root_folder):
        super().__init__()
        self.root = root_folder

    def format_folders(self) -> None:
        """
        Format the folder structure of the downloaded data from Sentinel Hub to a 
        digestible format, suitable for STAC metadata generation
        """
        sources = [dir for dir in listdir(self.root) if 'sen12floods' in dir]

        # Format the downloaded data directory structure
        for _source in sources:
            source = join(self.root, _source)   # abspath
            images_dirs = [image for image in listdir(source) if 'DS_Store' not in image]
            for _image in images_dirs:
                image_dir = join(source, _image)   # abspath
                split = _image.split('_')
                location_id = split[1]
                # There is no date for DEM data
                if len(split) >= 3:
                    date = split[2]
                    date_format = date.replace('-', '_')
                else:
                    date, date_format = None, None

                # Get response tiff
                _response_tiff = glob(f"{image_dir}/*/*.tiff")
                # If there is no response.tiff in the folder, skip it
                if not _response_tiff:
                    continue
                response_tiff = _response_tiff[0]

                # Create new destination folder
                dst_folder = join(source, f'{_source}_{location_id}')
                if date_format:
                    dst_folder = f'{dst_folder}_{date_format}'

                # If the destination folder already exists, skip it
                if exists(dst_folder):
                    continue
                mkdir(dst_folder)

                # Generate a metadata.json file of the raster in the destination folder. 
                # It will be used later for the STAC generation
                generate_raster_metadata(response_tiff, dst_folder, date)

                # Copy the response tiff to the destination folder giving a name 
                # indicating the mission
                if 'sentinel-1' in image_dir:
                    copyfile(response_tiff, join(dst_folder, 'SAR.tiff'))
                elif 'sentinel-2' in image_dir:
                    copyfile(response_tiff, join(dst_folder, 'SENTINEL-2.tiff'))
                elif 'dem' in image_dir:
                    copyfile(response_tiff, join(dst_folder, 'DEM.tiff'))

                # Remove the old image folder
                rmtree(image_dir)
