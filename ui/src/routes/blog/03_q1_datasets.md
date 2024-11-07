---
title: Working with Q1 datasets
date: '2023-11-04T03:00:00.000Z'
description: In this post you will learn how to work with STAC metadata to create Q1 datasets.
tags: STAC, Q1, datasets
link: https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/03_q1_datasets.ipynb
---

# Q1 Training Datasets

Training Datasets (TDS) in EOTDL are categorized into different [quality levels](https://eotdl.com/docs/datasets/quality), which in turn will impact the range of functionality that will be available for each dataset.

In this tutorial you will learn about Q1 datsets, datasets with STAC metadata. 

To ingest a Q1 datasets you will need its STAC metadata.

Some datasets already have STAC metadata, and can be ingested directly into EOTDL. However, in case that your dataset does not have STAC metadata but you want to ingest it as a Q1 dataset, the EOTDL library also offers functionality to create the metadata. Let's see an example using the EuroSAT dataset. 


```python
from eotdl.datasets import download_dataset

download_dataset("EuroSAT-RGB", version=1, path="data", force=True)
```

    100%|██████████| 90.3M/90.3M [00:04<00:00, 22.5MiB/s]
    100%|██████████| 2/2 [00:04<00:00,  2.30s/file]





    'data/EuroSAT-RGB/v1'




```python
!ls data/EuroSAT-RGB/v1
```

    EuroSAT-RGB.zip  metadata.yml



```python
!unzip -q data/EuroSAT-RGB/v1/EuroSAT-RGB.zip -d data/EuroSAT-RGB
```

The EuroSAT dataset contains satellite images for classification, i.e. each image has one label associated. In this case, the label can be extracted from the folder structure.


```python
import os 

labels = os.listdir('data/EuroSAT-RGB/2750')
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

os.makedirs('data/EuroSAT-RGB-small/', exist_ok=True)
for label in labels:
    os.makedirs('data/EuroSAT-RGB-small/' + label, exist_ok=True)
    images = os.listdir('data/EuroSAT-RGB/2750/' + label)[:10]
    for image in images:
        shutil.copy('data/EuroSAT-RGB/2750/' + label + '/' + image, 'data/EuroSAT-RGB-small/' + label + '/' + image)
```

You can use the `STACGenerator` to create the STAC metadata for your dataset in the form of a dataframe. The item parser will depend on the structure of your dataset. We offer some predefined parsers for common datasets, but you can also create your own parser.


```python
from eotdl.curation.stac.parsers import UnestructuredParser
from eotdl.curation.stac.stac import STACGenerator
from eotdl.curation.stac.dataframe_labeling import LabeledStrategy

stac_generator = STACGenerator(image_format='jpg', item_parser=UnestructuredParser, labeling_strategy=LabeledStrategy)

df = stac_generator.get_stac_dataframe('data/EuroSAT-RGB-small')
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
      <td>data/EuroSAT-RGB-small/Industrial/Industrial_1...</td>
      <td>Industrial</td>
      <td>0</td>
      <td>data/EuroSAT-RGB-small/source</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>1</th>
      <td>data/EuroSAT-RGB-small/Industrial/Industrial_1...</td>
      <td>Industrial</td>
      <td>0</td>
      <td>data/EuroSAT-RGB-small/source</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>2</th>
      <td>data/EuroSAT-RGB-small/Industrial/Industrial_1...</td>
      <td>Industrial</td>
      <td>0</td>
      <td>data/EuroSAT-RGB-small/source</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>3</th>
      <td>data/EuroSAT-RGB-small/Industrial/Industrial_1...</td>
      <td>Industrial</td>
      <td>0</td>
      <td>data/EuroSAT-RGB-small/source</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>4</th>
      <td>data/EuroSAT-RGB-small/Industrial/Industrial_1...</td>
      <td>Industrial</td>
      <td>0</td>
      <td>data/EuroSAT-RGB-small/source</td>
      <td>None</td>
      <td>None</td>
    </tr>
  </tbody>
</table>
</div>



Now we save the STAC metadata. The `id` given to the STAC catalog will be used as the name of the dataset in EOTDL (which has the same requirements than can be found in the [documentation](/docs/datasets/ingest)).


```python
output = 'data/EuroSAT-RGB-small-STAC'
stac_generator.generate_stac_metadata(stac_id='EuroSAT-RGB-Q1', description='EuroSAT-RGB dataset', stac_dataframe=df, output_folder=output)
```

    /home/juan/miniconda3/envs/eotdl/lib/python3.8/site-packages/rasterio/__init__.py:304: NotGeoreferencedWarning: Dataset has no geotransform, gcps, or rpcs. The identity matrix will be returned.
      dataset = DatasetReader(path, driver=driver, sharing=sharing, **kwargs)


    Generating source collection...


    100%|██████████| 100/100 [00:00<00:00, 972.12it/s]

    Validating and saving catalog...
    Success!


    


And, optionally, the labels using the labels extension.


```python
from eotdl.curation.stac.extensions.label import ImageNameLabeler

catalog = output + '/catalog.json'
labels_extra_properties = {'label_properties': ["label"],
                          'label_methods': ["manual"],
                          'label_tasks': ["classification"]}

labeler = ImageNameLabeler()
labeler.generate_stac_labels(catalog, stac_dataframe=df, **labels_extra_properties)
```

    Generating labels collection...


    100it [00:00, 2549.64it/s]


    Success on labels generation!


Once the STAC metadata is generated, we can ingest the dataset into EOTDL.


```python
from eotdl.datasets import ingest_dataset

ingest_dataset('data/EuroSAT-RGB-small-STAC')
```

    Loading STAC catalog...
    New version created, version: 1


    100%|██████████| 200/200 [00:32<00:00,  6.13it/s]


    Ingesting STAC catalog...
    Done


After the ingestion, you can explore and stage your dataset like shown in the previous tutorial.


```python
from eotdl.datasets import retrieve_datasets

datasets = retrieve_datasets('EuroSAT')
datasets
```




    ['EuroSAT-RGB',
     'EuroSAT',
     'EuroSAT-RGB-STAC',
     'EuroSAT-STAC',
     'EuroSAT-small',
     'EuroSAT-RGB-Q1']




```python
from eotdl.datasets import download_dataset

dst_path = download_dataset('EuroSAT-RGB-Q1')
dst_path
```




    '/home/juan/.cache/eotdl/datasets/EuroSAT-RGB-Q1/v1'



By default it will only download the STAC metadata. In case you also want to download the actual data, you can use the `assets` parameter. 

> The `force` parameter will overwrite the dataset if it already exists.


```python
from eotdl.datasets import download_dataset

dst_path = download_dataset('EuroSAT-RGB-Q1', force=True, assets=True)
dst_path
```

    100%|██████████| 200/200 [00:31<00:00,  6.39it/s]





    '/home/juan/.cache/eotdl/datasets/EuroSAT-RGB-Q1/v1'



You will find the data in  the `assets` subfolder, where a subfolder for each items with its `id` will contain all the assets for that item.


```python
from glob import glob

glob(dst_path + '/assets/*.jpg')[:3]
```




    ['/home/juan/.cache/eotdl/datasets/EuroSAT-RGB-Q1/v1/assets/AnnualCrop_1033.jpg',
     '/home/juan/.cache/eotdl/datasets/EuroSAT-RGB-Q1/v1/assets/HerbaceousVegetation_1743.jpg',
     '/home/juan/.cache/eotdl/datasets/EuroSAT-RGB-Q1/v1/assets/HerbaceousVegetation_1977.jpg']



Alternatively, you can download an asset using its url.


```python
import json

with open(dst_path + '/EuroSAT-RGB-Q1/source/Highway_594/Highway_594.json', 'r') as f:
	data = json.load(f)

data['assets']
```




    {'Highway_594': {'href': 'https://api.eotdl.com/datasets/654502991c54ab3a79d81007/download/Highway_594.jpg',
      'type': 'image/jpeg',
      'title': 'Highway_594',
      'roles': ['data']}}




```python
from eotdl.datasets import download_file_url

url = data['assets']['Highway_594']['href']
download_file_url(url, 'data')
```




    'data/assets/Highway_594.jpg'


