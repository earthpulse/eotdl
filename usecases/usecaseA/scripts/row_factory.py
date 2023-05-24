from osgeo import gdal
from sys import argv, stdout
from glob import glob
from datetime import datetime

import json
import os


_x = lambda gt, xpix, ypix: gt[0] + xpix * gt[1] + ypix * gt[2];
_y = lambda gt, xpix, ypix: gt[3] + ypix * gt[5] + xpix * gt[4];


def main(directory=argv[1]):
    # 10 meter bands are considered for S2 BB
    # extraction due to increased spatial
    # resolution. Blue band by default.
    
    # SH expects BB in low-left // top-right format.
    # I guess someone should use rasterio then, instead
    # of gdal. However, rasterio's bounding box implementation
    # was found to be buggy, as it uses 1-indexed pixel coordinates
    # instead of 0-indexed. Making the max bounds inaccurate by 1
    # unit of resolution in each dimension.

    if directory.startswith("s2"): S2(directory); 
    elif directory.startswith("s1"): S1(directory);

    exit(0)


def S1(directory):
    path = os.path.join(directory, "*.tif")
    tif = glob(path)[0]

    name = os.path.basename(tif)
    dataset = gdal.Open(tif)
    geotran = dataset.GetGeoTransform()
    
    last_x = dataset.RasterXSize - 1
    last_y = dataset.RasterYSize - 1

    datestr = os.path.basename(directory).split('_')[4]
    date = datetime.strptime(datestr, '%Y%m%dT%H%M%S')    

    bounding_box_lb_rt = [_x(geotran, 0, last_y),
                          _y(geotran, 0, last_y),
                          _x(geotran, last_x, 0),
                          _y(geotran, last_x, 0)]
    
    print(date.date(), bounding_box_lb_rt, directory, sep=';')
    return


def S2(directory):
    
    # 10 meter bands are considered for S2 BB
    # extraction due to increased spatial
    # resolution. Blue band by default.
    
    path = os.path.join(directory, "B2.tif*")
    tif  = glob(path)[0]

    name = os.path.basename(tif)
    dataset = gdal.Open(tif)
    geotran = dataset.GetGeoTransform()
    
    last_x = dataset.RasterXSize - 1;
    last_y = dataset.RasterYSize - 1;
    
    bounding_box_lb_rt = [_x(geotran, 0, last_y),
                          _y(geotran, 0, last_y),
                          _x(geotran, last_x, 0),
                          _y(geotran, last_x, 0)]

    datestr = os.path.basename(directory).split('_')[0]
    date = datetime.strptime(datestr, "%Y%m%dT%H%M%S")

    print(date.date(), bounding_box_lb_rt, directory, sep=';')
    return


if __name__ == "__main__":
    main()

