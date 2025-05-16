import json
import numpy as np
import pandas as pd
import rasterio
import rasterio.features
from scipy import signal
from shapely import affinity
from shapely.geometry import Polygon
from pathlib import Path
import geopandas as gpd


def convert_shape_to_wgs84(poly, transform):
    a,b,c,d,e,f =  transform[:6]
    mat = (a,b,d,e,c,f)
    return affinity.affine_transform(poly, mat)

def get_vessel_shape(center, width, length, theta):
    """ Get the bounding box for a ship
    Args:
        center (float): Ship's center index (subpixel)
        width (float): Ship's width in pixel
        length (float): Ship's length in pixel
        theta (float): Ship's heading angle in radian
    Returns:
        (Shapely Polygon): Bounding box 
    """
    width = width/2
    length = length/2
    poly = Polygon([(-width, -length), (-width, length), (width, length),
                    (width, -length)])

    poly = affinity.rotate(poly, theta, 'center',  use_radians=True)
    poly = affinity.translate(poly, xoff=center[0], yoff=center[1])
    return poly


def center_cross_correlation(data, width, length, theta, upsample_factor):
    """ Approximate the center of the boat with a cross correlation of the data
    and a gaussian model
    Args:
        data (Rasterio DatasetReader): tif file reader
        width (float): Ship's width in pixel
        length (float): Ship's length in pixel
        theta (float): Ship's heading angle in radian
        upsample_factor (uint): up sampling factor
    Returns:
        (Numpy Array):  centered mask
        (Numpy Array):  Correlations with each bands of the image
        (Numpy Array):  Coordinates of the center of the boat
    """
    # Up sampling
    up_sampled_data = np.repeat(np.repeat(data, upsample_factor, axis=1),
                                    upsample_factor, axis=0)
  
    # Rectangular mask
    size = (data.shape[0]*upsample_factor, data.shape[1]*upsample_factor)
    shape = get_vessel_shape([size[0]/2, size[1]/2], width * upsample_factor, length*upsample_factor, theta)
    centered_mask = rasterio.features.rasterize([shape], out_shape=(size), all_touched=True).astype(np.int8)

    # Remove null edges of the mask
    border_padding_size = 2 * upsample_factor
    max_x = int(np.max(shape.exterior.coords.xy[1])) +3 + border_padding_size
    min_x = int(np.min(shape.exterior.coords.xy[1])) -2 - border_padding_size
    max_y = int(np.max(shape.exterior.coords.xy[0])) +3 + border_padding_size
    min_y = int(np.min(shape.exterior.coords.xy[0])) -2 - border_padding_size

    if (max_x - min_x)%2 == 0:
        max_x += 1
    if (max_y - min_y)%2 == 0:
        max_y += 1

    cropped_mask = centered_mask[min_x:max_x, min_y:max_y]
    background_value = -1
    
    ####
    background_value = 0
    cropped_mask[cropped_mask == 0 ] = -1
    ####
    


    model_mask = cropped_mask.copy()
    model_mask[0:border_padding_size] = background_value
    model_mask[-border_padding_size:] = background_value
    model_mask[:,0:border_padding_size] = background_value
    model_mask[:,-border_padding_size:] = background_value
    for i in range(2,model_mask.shape[0]-2):
        for j in range(2, model_mask.shape[1]-2):
            window = cropped_mask[i-2:i+3,j-2:j+3]
            if np.all(window != 1):
                model_mask[i,j] = background_value

    # Model and data must have the same dimensions parity to avoid an offset after the cross correlation
    if model_mask.shape[0] %2 == 0:
        model_mask = np.append(model_mask, -1* np.ones((1, model_mask.shape[1])), axis=0)
    if model_mask.shape[1] %2 == 0:
        model_mask = np.append(model_mask, -1* np.ones((model_mask.shape[0],1)), axis=1)

    # Compute the coordinates of the maximum correlation for each band
    mean_filter = np.ones(cropped_mask.shape)/np.size(cropped_mask)
    correlations = np.zeros(up_sampled_data.shape)
    for i in range(data.shape[2]):
        correlation_band_i = signal.correlate2d(up_sampled_data[:, :, i],
                                                   model_mask, mode='valid', boundary='fill', fillvalue=0)
        
        # Mean filter convolution (removes abnormal high values)
        average_map = signal.convolve2d(up_sampled_data[:, :, i],
                                        mean_filter, mode='valid', boundary='fill', fillvalue=np.inf)  
        correlation_band_i = np.divide(correlation_band_i, average_map, 
                out=np.zeros(correlation_band_i.shape), where=average_map!=0) 
        correlation_band_i -= np.min(correlation_band_i)

        # resize the output
        nb = correlations.shape[0]
        na = correlation_band_i.shape[0]
        lowerx = (nb) // 2 - (na // 2)
        upperx = (nb // 2) + (na // 2)
        nb = correlations.shape[1]
        na = correlation_band_i.shape[1]
        lowery = (nb) // 2 - (na // 2)
        uppery = (nb // 2) + (na // 2)
        correlations[lowerx:upperx, lowery:uppery,i] = correlation_band_i


    window1d = np.abs(np.hamming(correlations.shape[0]))
    window2d = np.sqrt(np.outer(window1d,window1d))
    correlations *= np.repeat(window2d[:,:,None],correlations.shape[2],axis=2)

    somme = np.sum(correlations, axis = 2)
    
    ##########################################################

    

    center =  np.argwhere(somme == np.max(somme))[0] / upsample_factor

    # swap to the right coordinate system
    center[0], center[1] = center[1], center[0]

    return centered_mask, correlations, center


def generate_mask(file_path, output_dir, row_vessel, upsample_factor=1, output_type="raster", dilatation=5):
    """ Get the entries for the csv file for an image without a mask
    Args:
        file_path (String): path to the image
        output_dir (String): path to the output folder
        row_vessel (Pandas Dataframe): boat's informations
        upsample_factor (Int): upsampling factor for the model and the cross correlation
        output_type (String): can be a 'raster' (.tif) or a 'vector' (.geojson) output
        dilatation (Int): size of the dilation for the length and width of the mask in meters
    Returns:
        (Dict): csv entries for the image  
    """
    
    #  Load the source tile
    with rasterio.open(file_path, 'r') as src:

        # All 10m channels except blue
        data = src.read([2,3,4,11,12]).transpose(1, 2, 0)
        
        # Get the dimensions of the boat
        # pixel_res = abs(src.transform[4])
        pixel_res = 10
        width_px = row_vessel["Width"] / pixel_res
        length_px = row_vessel["Length"] / pixel_res

        # Get the center of the mask
        model, correlations, center = center_cross_correlation(data,
                width_px, length_px, row_vessel['Heading'], upsample_factor)

        # Rectangular bounding box
        mask_width_px = (row_vessel["Width"] + dilatation) / pixel_res
        mask_length_px = (row_vessel["Length"] + dilatation) / pixel_res
        shape = get_vessel_shape(center, mask_width_px, mask_length_px, row_vessel['Heading'])
        mask = rasterio.features.rasterize([shape], out_shape=data.shape[0:2], all_touched=True)

        if output_type == "vector":
            # generate Geojson  
            shape_wgs84 = convert_shape_to_wgs84(shape, src.transform)
            gdr = gpd.GeoDataFrame({'geometry': [shape_wgs84],  
                                "labels": [["Boat"]], 
                                "tasks":[["segmentation"]]}, 
                                crs='EPSG:4326')

            # Write to geojson
            label_geojson = gdr.to_json(drop_id=True)
            out_mask_path = Path(file_path).parent / f"{file_path.stem}_labels.geojson"

            with open(out_mask_path, "w") as dst:
                dst.write(label_geojson)

        elif output_type == "raster":
            # Create the profile for the .tif
            profile = {
                'driver': 'GTiff',
                'height': src.height,
                'width': src.width,
                'count': 1,
                'dtype': rasterio.uint8,
                'crs': src.crs,
                'transform': src.transform,
                'nodata': None,
                'compress': 'lzw'
            }

            # Write the mask
            out_mask_path = Path(output_dir) / f"mask_{Path(file_path).name}"
            with rasterio.open(out_mask_path, 'w', **profile) as dst:
                dst.write(mask, indexes=1)


def process_directoy(dir_name, output_dir, tiles_df, upsample_factor, output_type):

    assert output_type == "raster" or output_type == "vector"
    print(f"Processing tiles from {dir_name}")

    # Prepare outputpath
    output_dir_name = Path(output_dir)

    if output_type =="vector":

        labels_json = {"labels": [{"name": "Boat", "color": "#ff8000"}]}
        json_path = Path(dir_name) / "labels.json"

        with open(json_path, "w") as dst:
            dst.write(json.dumps(labels_json))

    # Generate the mask for each vessel
    list_nan = []

    # Convert angles in radian
    tiles_df["Heading"] *= np.pi/180

    for i in range(len(tiles_df)):
        row_vessel = tiles_df.iloc[i]
        img_path = Path(dir_name) / f"{row_vessel['ImageId']}.tiff"

        # Get mmsi from filename
        vessel = int(row_vessel["ImageId"].split('_')[1])
        
        if row_vessel.isnull().values.any(): # Tiles with Nan data
            list_nan.append(vessel)
        
        else:
            # Get the mask of the boat
            generate_mask(img_path, output_dir_name, row_vessel, upsample_factor, output_type)
        
    if list_nan:
        print(f"No mask saved for the vessels {list_nan}, NaN values found in the AIS data")


def process_db(images_path, output_dir, upsample_factor, output_type = "raster"):
    """ Get the entries for the csv file for an image without a mask
    Args:
        csv_tiles (String): path to the csv folder of the tiles
        output_dir (String): path to the output folder
        upsample_factor (Int): upsampling factor for the model and the cross correlation
        output_type (String): can be a 'raster' (.tif) or a 'vector' (.geojson) output
    """
    # Prepare the output file
    csv_paths = Path(images_path).glob("*.csv")
    for csv_tiles in csv_paths:
        # read the tiles csv
        tiles_df = pd.read_csv(csv_tiles)
        # Get the path to the tiles
        tiles_path = Path(csv_tiles).parent
        process_directoy(tiles_path,
                         output_dir=output_dir, 
                         tiles_df=tiles_df, 
                         upsample_factor=upsample_factor,
                         output_type=output_type)
