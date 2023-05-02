"""
Module for formatter classes
"""

from os.path import join
from os import listdir, mkdir

from shutil import rmtree, copyfile

import rasterio


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
                                 raster: rasterio.DatasetReader, 
                                 output_folder: str
                                 ) -> None:
        """
        Extract the bands of a Sentinel-1 image into a desired output
        folder
        
        :param raster: Sentinel-1 image to extract the bands from
        :param output_folder: output folder to write the bands to
        """
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
                                 raster: rasterio.DatasetReader, 
                                 output_folder: str
                                 ) -> None:
        """
        Extract the bands of a Sentinel-2 image into a desired output
        folder
        
        :param raster: Sentinel-2 image to extract the bands from
        :param output_folder: output folder to write the bands to
        """
        # the +1 allows the writing of the last band
        for band in range(1, raster.count + 1):
            single_band = raster.read(band)

            band_name = f'B{str(band)}.tiff'
            ds_out = join(output_folder, band_name)

            # Copy the metadata
            metadata = raster.meta.copy()
            metadata.update({"count": 1})

            with rasterio.open(ds_out, "w", **metadata) as dest:
                dest.write(single_band, 1)


bands_formatter = SHBandsFormatter()


class SHFolderFormatter(Formatter):
    """
    Class for formatting the directories of Sentinel images
    downloaded from Sentinel Hub Services
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
            images = [image for image in listdir(source) if 'DS_Store' not in image]
            for _image in images:
                image = join(source, _image)   # abspath
                split = _image.split('_')
                location_id = split[1]
                # There is no date for DEM data
                date = split[2].replace('-', '_') if len(split) >= 3 else None

                # Get response files
                _request_folder = [f for f in listdir(image) if 'DS_Store' not in f][0]
                request_folder = join(image, _request_folder)
                response_json = join(request_folder, 'request.json')
                response_tiff = join(request_folder, 'response.tiff')
                
                # Create new destination folder
                dst_folder = join(source, f'{_source}_{location_id}')
                if date:
                    dst_folder = f'{dst_folder}_{date}'

                try:
                    mkdir(dst_folder)
                except FileExistsError:
                    rmtree(dst_folder)
                    mkdir(dst_folder)
                    
                # Maintain the request.json file, as it has important info that we will
                # need for STAC generation
                copyfile(response_json, join(dst_folder, 'request.json'))
                
                # Open the rasters and extracts the bands as independent files
                ds = rasterio.open(response_tiff)
                
                if 'sentinel-1' in image:
                    bands_formatter.extract_sentinel_1_bands(ds, dst_folder)
                elif 'sentinel-2' in image:
                    bands_formatter.extract_sentinel_2_bands(ds, dst_folder)
                elif 'dem' in image:
                    # No need to extract bands for DEM data, just copy the file
                    copyfile(response_tiff, join(dst_folder, 'DEM.tiff'))

                # Remove the old image folder
                rmtree(image)
