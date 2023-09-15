---
title: Q1 Training Datasets
date: '2023-09-15T00:00:00.000Z'
description: In this post you will learn about Q1 datssets and how to create and ingest them in EOTDL.
tags: Q1, datasets
---

# Q1 Training Datasets

Training Datasets (TDS) in EOTDL are categorized into different [quality levels](https://eotdl.com/docs/datasets/quality), which in turn will impact the range of functionality that will be available for each dataset.

In this tutorial you will learn about Q1 datsets, datasets with STAC metadata. 

## Ingesting Q1 datasets

To ingest a Q1 datasets you will need its STAC metadata.


Some datasets already have STAC metadata, and can be ingested directly into EOTDL. However, in case that your dataset does not have STAC metadata but you want to ingest it as a Q1 dataset, the EOTDL library also offers functionality to create the metadata. Let's see an example using the EuroSAT dataset. You can download the dataset [here](https://www.eotdl.com/datasets/EuroSAT-RGB). Then, extract it and put it in the `data` folder.


```python
import os 

os.listdir('data')
```




    ['EuroSAT']



The EuroSAT dataset contains satellite images for classification, i.e. each image has one label associated. In this case, the label can be extracted from the folder structure.


```python
labels = os.listdir('data/EuroSAT/2750')
labels
```




    ['Industrial',
     'Forest',
     'HerbaceousVegetation',
     'PermanentCrop',
     'Highway',
     'Residential',
     'SeaLake',
     'River',
     'AnnualCrop',
     'Pasture']



For faster processing, we will generate a copy of the dataset with only 10 images per class.


```python
import shutil 

os.makedirs('data/EuroSAT-small/', exist_ok=True)
for label in labels:
    os.makedirs('data/EuroSAT-small/' + label, exist_ok=True)
    images = os.listdir('data/EuroSAT/2750/' + label)[:10]
    for image in images:
        shutil.copy('data/EuroSAT/2750/' + label + '/' + image, 'data/EuroSAT-small/' + label + '/' + image)
```

You can use the `STACGenerator` to create the STAC metadata for your dataset in the form of a dataframe. The item parser will depend on the structure of your dataset. We offer some predefined parsers for common datasets, but you can also create your own parser.

> TODO: How to create a parser.


```python
from eotdl.curation.stac.parsers import UnestructuredParser
from eotdl.curation.stac.stac import STACGenerator

stac_generator = STACGenerator(image_format='jpg', item_parser=UnestructuredParser)

df = stac_generator.get_stac_dataframe('data/EuroSAT-small')
df.head()

```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>image</th>
      <th>label</th>
      <th>ix</th>
      <th>collection</th>
      <th>extensions</th>
      <th>bands</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>data/EuroSAT-small/Industrial/Industrial_1743.jpg</td>
      <td>Industrial</td>
      <td>0</td>
      <td>data/EuroSAT-small/source</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>1</th>
      <td>data/EuroSAT-small/Industrial/Industrial_1273.jpg</td>
      <td>Industrial</td>
      <td>0</td>
      <td>data/EuroSAT-small/source</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>2</th>
      <td>data/EuroSAT-small/Industrial/Industrial_1117.jpg</td>
      <td>Industrial</td>
      <td>0</td>
      <td>data/EuroSAT-small/source</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>3</th>
      <td>data/EuroSAT-small/Industrial/Industrial_1121.jpg</td>
      <td>Industrial</td>
      <td>0</td>
      <td>data/EuroSAT-small/source</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>4</th>
      <td>data/EuroSAT-small/Industrial/Industrial_1641.jpg</td>
      <td>Industrial</td>
      <td>0</td>
      <td>data/EuroSAT-small/source</td>
      <td>None</td>
      <td>None</td>
    </tr>
  </tbody>
</table>
</div>



Now we save the STAC metadata. The `id` given to the STAC catalog will be used as the name of the dataset in EOTDL (which has the same requirements than can be found in the [documentation](/docs/datasets/ingest)).


```python
output = 'data/EuroSAT-STAC'
stac_generator.generate_stac_metadata(id='eurosat-rgb', description='EuroSAT-RGB dataset', stac_dataframe=df, output_folder=output)
```

   


    Generating source collection...
    Validating and saving catalog...
    Success!


    


And, optionally, the labels using the labels extension.


```python
catalog = output + '/catalog.json'
stac_generator.generate_stac_labels(catalog)
```

    Generating labels collection...

Once the STAC metadata is generated, we can ingest the dataset into EOTDL.


```python
from eotdl.datasets import ingest_dataset

ingest_dataset('data/EuroSAT-STAC')
```

    Loading STAC catalog...
    Uploading assets...


    100%|██████████| 200/200 [00:39<00:00,  5.12it/s]


    Ingesting STAC catalog...
    Done



After the ingestion, you can explore and download your dataset like shown in the previous tutorial.


```python
from eotdl.datasets import list_datasets

datasets = list_datasets()
datasets
```




    ['eurosat-rgb',
     'eurosat-rgb-q2',
     'COWC',
     'Stanford-Drone-dataset',
     'EuroSAT-RGB-STAC',
     'EuroSAT-STAC',
     'BigEarthNet',
     'xview2',
     'LandcoverAI',
     'open-cities-tt2-source',
     'open-cities-tt1-source',
     'open-cities-test',
     'PASTIS-R',
     'EuroCrops',
     'SloveniaLandCover',
     'ISPRS-Potsdam2D',
     'SEN12-FLOOD',
     'Urban3dChallenge',
     'tropical-cyclone-dataset',
     'Vessel-detection',
     'Airplanes-detection',
     'S2-SHIPS',
     'SpaceNet-7',
     'Sentinel-2-Cloud-Mask',
     'PASTIS',
     'FlodNet',
     'SeCo100k',
     'SeCo',
     'AirbusAircraftDetection',
     'AirbusWindTurbinesPatches',
     'RoadNet',
     'EuroSAT',
     'UCMerced',
     'EuroSAT-RGB']




```python
from eotdl.datasets import download_dataset

dst_path = download_dataset('eurosat-rgb')
dst_path
```

    Downloading STAC metadata...
    To download assets, set assets=True or -a in the CLI.



By default it will only download the STAC metadata. In case you also want to download the actual data, you can use the `assets` parameter. 

> The `force` parameter will overwrite the dataset if it already exists.


```python
from eotdl.datasets import download_dataset

dst_path = download_dataset('eurosat-rgb', force=True, assets=True)
dst_path
```

    Downloading STAC metadata...
    Downloading assets...


    100%|██████████| 200/200 [00:34<00:00,  5.85it/s]




You will find the data in  the `assets` subfolder, where a subfolder for each items with its `id` will contain all the assets for that item.


```python
from glob import glob

glob(dst_path + '/assets/**/*.jpg')[:3]
```




    ['/home/juan/.cache/eotdl/datasets/eurosat-rgb/assets/River_1655/River_1655.jpg',
     '/home/juan/.cache/eotdl/datasets/eurosat-rgb/assets/AnnualCrop_1142/AnnualCrop_1142.jpg',
     '/home/juan/.cache/eotdl/datasets/eurosat-rgb/assets/Industrial_435/Industrial_435.jpg']



Alternatively, you can download an asset using its url.


```python
import json

with open(dst_path + '/eurosat-rgb/source/Highway_594/Highway_594.json', 'r') as f:
	data = json.load(f)

data['assets']
```




    {'Highway_594': {'href': 'https://api.eotdl.com/datasets/6503f8a3d05a1b62cc273ea4/download/Highway_594.jpg',
      'type': 'image/jpeg',
      'title': 'Highway_594',
      'roles': ['data']}}




```python
from eotdl.datasets import download_file_url

url = data['assets']['Highway_594']['href']
download_file_url(url, 'data')
```

    100%|██████████| 4.07k/4.07k [00:00<00:00, 743kiB/s]





    'data/Highway_594.jpg'


