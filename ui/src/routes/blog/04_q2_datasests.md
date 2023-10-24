---
title: Q2 Training Datasets
date: '2023-09-15T10:00:00.000Z'
description: In this post you will learn about Q2 datasets and how to create and ingest them in EOTDL.
tags: Q1, datasets
---

🚧 Under development, Q2 datasets are not yet stable. Let us know if you find any issue!

# Q2 Training Datasets

Training Datasets (TDS) in EOTDL are categorized into different [quality levels](https://eotdl.com/docs/datasets/quality), which in turn will impact the range of functionality that will be available for each dataset.

In this tutorial you will learn about Q2 datsets, datasets with STAC metadata and EOTDL's custom STAC extensions. 

## The ML-Dataset Extension

The main extension used by EOTDL for Q2 datasets is the ML-Dataset extension. It enhances the STAC metadata of a dataset including information such as data splits (train, validation, test), quality metrics, etc.

Let's see how to generate a Q2 dataset using the EOTDL library for the EuroSAT dataset. Q2 datasets are generated from Q1 datasets, datasets with STAC metadata. We already showed how to generate a Q1 dataset in the previous tutorial.


```python
import os 

os.listdir('data')
```




    ['EuroSAT',
     'EuroSAT-STAC']




```python
from eotdl.curation.stac.ml_dataset import add_ml_extension

catalog = 'data/EuroSAT-STAC/catalog.json'

add_ml_extension(
	catalog,
	destination='data/EuroSAT-Q2',
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
    Total size: 99
    Train size: 79
    Test size: 9
    Validation size: 9
    Generating Training split...
    Generating Validation split...
    Generating Test split...
    Success on splits generation!
    Validating and saving...
    Success!


    


When ingesting a Q2 dataset, EOTDL will automatically compute quality metrics on your dataset, that will be reported in the metadata. Optionally, you can compute them to analyse your dataset before ingesting it.


```python
from eotdl.curation.stac.ml_dataset import MLDatasetQualityMetrics

catalog = 'data/EuroSAT-Q2/catalog.json'

MLDatasetQualityMetrics.calculate(catalog)
```

    Looking for spatial duplicates...
    Calculating classes balance...
    Validating and saving...
    Success!


    


Remember, however, that the metrics will be computed automatically when ingesting the dataset, so you don't need to do it yourself. These metrics incude aspects such as the number of samples, duplicates, missing values, class imbalance, etc.

## Ingesting Q2 datasets

Once the metadata has been generated, you can ingest, explore and download a Q2 dataset as any other dataset.


```python
from eotdl.datasets import ingest_dataset

ingest_dataset('data/EuroSAT-Q2')
```

    Loading STAC catalog...
    Uploading assets...
    Ingesting STAC catalog...
    Done


