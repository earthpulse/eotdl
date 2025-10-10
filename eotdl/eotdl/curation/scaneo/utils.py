import geopandas as gpd
import rasterio as rio
from rasterio.features import rasterize
from tqdm import tqdm
import json
import os
from glob import glob

def generate_masks_from_labels(path, verbose=True):

    labels_path = os.path.join(path, 'spai.json')
    if not os.path.exists(labels_path):
        raise FileNotFoundError(f"Labels file not found at {labels_path}")

    with open(labels_path, 'r') as f:
        spai_labels = json.load(f)
    colors = {label['name']: label['color'] for label in spai_labels['labels']}

    labels = sorted(glob(os.path.join(path, '*.geojson')))
    for _label in tqdm(labels):
        label = gpd.read_file(_label)
        seg = label[label['task'] == 'segmentation']
        if len(seg) == 0:
            if verbose:
                print(f"No segmentation labels found for {_label}")
            continue
        image = _label.replace('geojson', 'tif')
        if not os.path.exists(image):
            print(f"Image {image} not found for label {_label}")
            continue
        with rio.open(image) as ds:
            # target shape and transform
            out_shape = (ds.height, ds.width)
            transform = ds.transform
            # prepare (geometry, index) pairs
            # here we enumerate so indices start at 1; 0 will be background
            shapes = (
                (row.geometry, list(colors.keys()).index(row['label']) + 1)
                for _, row in seg.to_crs(ds.crs).iterrows()
            )
            # rasterize: background=0, polygons get their index
            mask = rasterize(
                shapes=shapes,
                out_shape=out_shape,
                transform=transform,
                fill=0,
                dtype='uint8',  # or 'uint16' if you have >255 polygons
            )
            # Save the mask with the same name as the image but with _mask suffix
            mask_path = image.replace('.tif', '_mask.tif')
            with rio.open(
                mask_path,
                'w',
                driver='GTiff',
                height=mask.shape[0],
                width=mask.shape[1],
                count=1,
                dtype=mask.dtype,
                crs=ds.crs,
                transform=transform,
            ) as dst:
                dst.write(mask, 1)