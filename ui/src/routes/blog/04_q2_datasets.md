---
title: Working with Q2 datasets
date: '2023-11-04T04:00:00.000Z'
description: In this post you will learn how to work with STAC metadata to create Q2 datasets.
tags: STAC, Q2, datasets
link: https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/04_q2_datasets.ipynb
---

# Q2 Training Datasets

Training Datasets (TDS) in EOTDL are categorized into different [quality levels](https://eotdl.com/docs/datasets/quality), which in turn will impact the range of functionality that will be available for each dataset.

In this tutorial you will learn about Q2 datsets, datasets with STAC metadata and EOTDL's custom STAC extensions. 

## The ML-Dataset Extension

The main extension used by EOTDL for Q2 datasets is the ML-Dataset extension. It enhances the STAC metadata of a dataset including information such as data splits (train, validation, test), quality metrics, etc.

Let's see how to generate a Q2 dataset using the EOTDL library for the EuroSAT dataset. Q2 datasets are generated from Q1 datasets, datasets with STAC metadata. We already showed how to generate a Q1 dataset in the previous tutorial.


```python
import os 

os.listdir('example_data')
```




    ['jaca_dataset_q2',
     'sample_stacdataframe.csv',
     'jaca_dataset',
     'labels_scaneo',
     'eurosat_rgb_stac',
     'jaca_dataset_stac',
     'EuroSAT-RGB-small',
     'eurosat_rgb_dataset',
     'EuroSAT-small',
     'EuroSAT-RGB-small-STAC',
     'eurosat_rgb_stac_labels',
     'jaca_dataset_stac_labels']




```python
from eotdl.curation.stac.extensions import add_ml_extension

catalog = 'example_data/EuroSAT-RGB-small-STAC/catalog.json'

add_ml_extension(
	catalog,
	destination='data/EuroSAT-RGB-Q2',
	splits=True,
	splits_collection_id="labels",
	name='EuroSAT Q2 Dataset',
	tasks=['image classification'],
	inputs_type=['satellite imagery'],
	annotations_type='raster',
	version='0.1.0'
)
```

    Generating splits...
    Total size: 100
    Train size: 80
    Test size: 10
    Validation size: 10
    Generating Training split...


    100%|██████████| 80/80 [00:00<00:00, 4967.64it/s]


    Generating Validation split...


    100%|██████████| 10/10 [00:00<00:00, 3880.02it/s]


    Generating Test split...


    100%|██████████| 10/10 [00:00<00:00, 5876.84it/s]

    Success on splits generation!
    Validating and saving...


    


    Success!


When ingesting a Q2 dataset, EOTDL will automatically compute quality metrics on your dataset, that will be reported in the metadata. Optionally, you can compute them to analyse your dataset before ingesting it.


```python
from eotdl.curation.stac.extensions import MLDatasetQualityMetrics

catalog = 'data/EuroSAT-RGB-Q2/catalog.json'

MLDatasetQualityMetrics.calculate(catalog)
```

    Looking for spatial duplicates...: 400it [00:00, 6256.56it/s]
    Calculating classes balance...: 400it [00:00, 196110.06it/s]

    Validating and saving...
    Success!


    


Remember, however, that the metrics will be computed automatically when ingesting the dataset, so you don't need to do it yourself. These metrics incude aspects such as the number of samples, duplicates, missing values, class imbalance, etc.

## Ingesting Q2 datasets

Once the metadata has been generated, you can ingest, explore and download a Q2 dataset as any other dataset.


```python
from eotdl.datasets import ingest_dataset

ingest_dataset('data/EuroSAT-RGB-Q2')
```

    Loading STAC catalog...
    New version created, version: 1


    100%|██████████| 400/400 [00:59<00:00,  6.71it/s]


    Ingesting STAC catalog...
    Done

