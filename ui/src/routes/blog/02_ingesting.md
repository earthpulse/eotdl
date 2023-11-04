---
title: Ingesting Datasets and Models
date: '2023-11-04T02:00:00.000Z'
description: In this post you will learn how to ingest datasets and models to the EOTDL
tags: getting started, ingest, datasets, models
link: https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/02_ingesting.ipynb
---

# Ingest an existing Dataset or Model

In this notebook we are going to showcase how to ingest an existing dataset or model into EOTDL.

Once it is ingested, you can use it in the same way as any other dataset or model in EOTDL (exploring, downloading, etc.).

## Ingesting through the CLI

The recommended way to ingest a dataset is using the CLI.


```python
!eotdl datasets ingest --help
```

    [1m                                                                                [0m
    [1m [0m[1;33mUsage: [0m[1meotdl datasets ingest [OPTIONS][0m[1m                                        [0m[1m [0m
    [1m                                                                                [0m
     Ingest a dataset to the EOTDL.                                                 
     [2mThis command ingests the dataset to the EOTDL. The dataset must be a folder [0m   
     [2mwith the dataset files, and at least a metadata.yml file or a catalog.json [0m    
     [2mfile. If there are not these files, the ingestion will not work. All the files[0m 
     [2min the folder will be uploaded to the EOTDL.[0m                                   
                                                                                    
     [2mThe following constraints apply to the dataset name:[0m                           
     [2m- It must be unique[0m                                                            
     [2m- It must be between 3 and 45 characters long[0m                                  
     [2m- It can only contain alphanumeric characters and dashes.[0m                      
                                                                                    
     [2mThe metadata.yml file must contain the following fields:[0m                       
     [2m- name: the name of the dataset[0m                                                
     [2m- authors: the author or authors of the dataset[0m                                
     [2m- license: the license of the dataset[0m                                          
     [2m- source: the source of the dataset[0m                                            
                                                                                    
     [2mIf using [0m[1;2;36m-[0m[1;2;36m-verbose[0m[2m, it will print the progress of the ingestion.[0m               
                                                                                    
     [2mExamples[0m                                                                       
     [1;2;36m--------[0m                                                                       
     [2m$ eotdl dataset ingest [0m[1;2;36m-[0m[1;2;36m-path[0m[2m /path/to/folder-with-dataset [0m[1;2;36m-[0m[1;2;36m-verbose[0m[2m True[0m      
                                                                                    
    [2m╭─[0m[2m Options [0m[2m───────────────────────────────────────────────────────────────────[0m[2m─╮[0m
    [2m│[0m [31m*[0m  [1;36m-[0m[1;36m-path[0m     [1;32m-p[0m      [1;33mPATH[0m  Path to the dataset to ingest [2m[default: None][0m    [2m│[0m
    [2m│[0m                             [2;31m[required]                   [0m                    [2m│[0m
    [2m│[0m    [1;36m-[0m[1;36m-verbose[0m          [1;33m    [0m  Verbose output. This will print the progress of  [2m│[0m
    [2m│[0m                             the ingestion                                    [2m│[0m
    [2m│[0m    [1;36m-[0m[1;36m-help[0m             [1;33m    [0m  Show this message and exit.                      [2m│[0m
    [2m╰──────────────────────────────────────────────────────────────────────────────╯[0m
    


In order to ingest a dataset you will need a folder in your system with the data you want to upload.


```python
!ls example_data
```

    eurosat_rgb_dataset	 jaca_dataset	    jaca_dataset_stac_labels
    eurosat_rgb_stac	 jaca_dataset_q2    labels_scaneo
    eurosat_rgb_stac_labels  jaca_dataset_stac  sample_stacdataframe.csv


For this tutorial we are going to work with a subsample of the [EuroSAT](https://www.eotdl.com/datasets/EuroSAT-RGB) dataset.


```python
from glob import glob 

files = glob('example_data/EuroSAT-small/**/*.*', recursive=True)
files
```




    ['example_data/EuroSAT-small/metadata.yml',
     'example_data/EuroSAT-small/Forest/Forest_3.tif',
     'example_data/EuroSAT-small/Forest/Forest_1.tif',
     'example_data/EuroSAT-small/Forest/Forest_2.tif',
     'example_data/EuroSAT-small/AnnualCrop/AnnualCrop_3.tif',
     'example_data/EuroSAT-small/AnnualCrop/AnnualCrop_1.tif',
     'example_data/EuroSAT-small/AnnualCrop/AnnualCrop_2.tif']



A `metadata.yml` file is required for Q0 datasets and models, containing some basic required information (dataset authors, licens, link to source and dataset name)


```python
!cat example_data/EuroSAT-small/metadata.yml
```

    authors:
    - Patrick Helber
    license: open
    source: http://madm.dfki.de/downloads
    name: EuroSAT-small


The chosen name is the one that will appear in the repository, hence it must be unique, between 3 and 45 characters long and can only contain alphanumeric characters and dashes (learn more at [https://www.eotdl.com/docs/datasets/ingest](https://www.eotdl.com/docs/datasets/ingest)).

Trying to ingest a dataset without a `metadata.yml` file will fail.

If everything is correct, the ingestion process should suceed.


```python
!eotdl datasets ingest -p example_data/EuroSAT-small/
```

    Uploading directory example_data/EuroSAT-small...
    generating list of files to upload...
    100%|███████████████████████████████████████████| 7/7 [00:00<00:00, 4106.31it/s]
    No new files to upload


And now your dataset is avilable at EOTDL


```python
!eotdl datasets list -n eurosat-small
```

    ['EuroSAT-small']


> Since the `EuroSAT-small` name is already taken, this process should fail for you. To solve it, just upload the dataset with a different name. However, this will polute the EOTDL with test datasets so we encourage you to try the ingestion process with a real dataset that you want to ingest (or overwrite your test dataset in the future with useful data).

In order to ingest Q1+ datasets, a valid STAC catalog is required instead of the `metadata.yml` file. 

You can ingest a model exactly in the same way


```python
!eotdl models ingest --help
```

    [1m                                                                                [0m
    [1m [0m[1;33mUsage: [0m[1meotdl models ingest [OPTIONS][0m[1m                                          [0m[1m [0m
    [1m                                                                                [0m
     Ingest a model to the EOTDL.                                                   
     [2mThis command ingests the model to the EOTDL. The model must be a folder with [0m  
     [2mthe model files, and at least a metadata.yml file or a catalog.json file. If [0m  
     [2mthere are not these files, the ingestion will not work. All the files in the [0m  
     [2mfolder will be uploaded to the EOTDL.[0m                                          
                                                                                    
     [2mThe following constraints apply to the model name:[0m                             
     [2m- It must be unique[0m                                                            
     [2m- It must be between 3 and 45 characters long[0m                                  
     [2m- It can only contain alphanumeric characters and dashes.[0m                      
                                                                                    
     [2mThe metadata.yml file must contain the following fields:[0m                       
     [2m- name: the name of the model[0m                                                  
     [2m- authors: the author or authors of the model[0m                                  
     [2m- license: the license of the model[0m                                            
     [2m- source: the source of the model[0m                                              
                                                                                    
     [2mIf using [0m[1;2;36m-[0m[1;2;36m-verbose[0m[2m, it will print the progress of the ingestion.[0m               
                                                                                    
     [2mExamples[0m                                                                       
     [1;2;36m--------[0m                                                                       
     [2m$ eotdl models ingest [0m[1;2;36m-[0m[1;2;36m-path[0m[2m /path/to/folder-with-model [0m[1;2;36m-[0m[1;2;36m-verbose[0m[2m True[0m         
                                                                                    
    [2m╭─[0m[2m Options [0m[2m───────────────────────────────────────────────────────────────────[0m[2m─╮[0m
    [2m│[0m [31m*[0m  [1;36m-[0m[1;36m-path[0m     [1;32m-p[0m      [1;33mPATH[0m  Path to the model to ingest [2m[default: None][0m      [2m│[0m
    [2m│[0m                             [2;31m[required]                 [0m                      [2m│[0m
    [2m│[0m    [1;36m-[0m[1;36m-verbose[0m          [1;33m    [0m  Verbose output. This will print the progress of  [2m│[0m
    [2m│[0m                             the ingestion                                    [2m│[0m
    [2m│[0m    [1;36m-[0m[1;36m-help[0m             [1;33m    [0m  Show this message and exit.                      [2m│[0m
    [2m╰──────────────────────────────────────────────────────────────────────────────╯[0m
    


## Versioning

By default, every time you re-upload a dataset or model a new version is created.

When you download a dataset, the latest version is used by default.


```python
!eotdl datasets get EuroSAT-small
```

    Dataset `EuroSAT-small v10` already exists at /home/juan/.cache/eotdl/datasets/EuroSAT-small/v10. To force download, use force=True or -f in the CLI.


However, you can specify the version


```python
!eotdl datasets get EuroSAT-small -v 1
```

    Dataset `EuroSAT-small v1` already exists at /home/juan/.cache/eotdl/datasets/EuroSAT-small/v1. To force download, use force=True or -f in the CLI.



```python
!ls $HOME/.cache/eotdl/datasets/EuroSAT-small
```

    v1  v10  v2  v3  v9


We apply versioning at dataset/model and file level, meaning only new or modified files will be uploaded in future re-uploads, downloading the appropriate files for each version.

You can explore the different versions in the user interface.

## Ingesting through the Library

You can ingest datasets and models using the library


```python
from eotdl.datasets import ingest_dataset

ingest_dataset("example_data/EuroSAT-small");
```

    Uploading directory example_data/EuroSAT-small...
    generating list of files to upload...


    100%|██████████| 7/7 [00:00<00:00, 6440.04it/s]



    ---------------------------------------------------------------------------

    Exception                                 Traceback (most recent call last)

    /home/juan/Desktop/eotdl/tutorials/notebooks/02_ingesting.ipynb Cell 29 line 3
          <a href='vscode-notebook-cell://ssh-remote%2Bharley/home/juan/Desktop/eotdl/tutorials/notebooks/02_ingesting.ipynb#X45sdnNjb2RlLXJlbW90ZQ%3D%3D?line=0'>1</a> from eotdl.datasets import ingest_dataset
    ----> <a href='vscode-notebook-cell://ssh-remote%2Bharley/home/juan/Desktop/eotdl/tutorials/notebooks/02_ingesting.ipynb#X45sdnNjb2RlLXJlbW90ZQ%3D%3D?line=2'>3</a> ingest_dataset("example_data/EuroSAT-small")


    File ~/miniconda3/envs/eotdl/lib/python3.8/site-packages/eotdl/datasets/ingest.py:16, in ingest_dataset(path, verbose, logger)
         13     raise Exception("Path must be a folder")
         14 # if "catalog.json" in [f.name for f in path.iterdir()]:
         15 #     return ingest_stac(path / "catalog.json", logger)
    ---> 16 return ingest_folder(path, verbose, logger)


    File ~/miniconda3/envs/eotdl/lib/python3.8/site-packages/eotdl/auth/auth.py:47, in with_auth.<locals>.wrapper(*args, **kwargs)
         45 def wrapper(*args, **kwargs):
         46     user = auth()
    ---> 47     return func(*args, **kwargs, user=user)


    File ~/miniconda3/envs/eotdl/lib/python3.8/site-packages/eotdl/datasets/ingest.py:44, in ingest_folder(folder, verbose, logger, user)
         42 dataset_id = retrieve_dataset(metadata, user)
         43 # ingest files
    ---> 44 return ingest_files(
         45     repo, dataset_id, folder, verbose, logger, user, endpoint="datasets"
         46 )


    File ~/miniconda3/envs/eotdl/lib/python3.8/site-packages/eotdl/files/ingest.py:102, in ingest_files(repo, dataset_or_model_id, folder, verbose, logger, user, endpoint)
        100 items = retrieve_files(folder)
        101 # retrieve files
    --> 102 upload_files, existing_files, large_files = generate_files_lists(
        103     items, folder, dataset_or_model_id, endpoint, logger
        104 )
        105 logger(f"{len(upload_files) + len(large_files)} new files will be ingested")
        106 logger(f"{len(existing_files)} files already exist in dataset")


    File ~/miniconda3/envs/eotdl/lib/python3.8/site-packages/eotdl/files/ingest.py:86, in generate_files_lists(items, folder, dataset_or_model_id, endpoint, logger, max_size)
         84             upload_files.append(data)
         85 if len(upload_files) == 0 and len(large_files) == 0:
    ---> 86     raise Exception("No new files to upload")
         87 return upload_files, existing_files, large_files


    Exception: No new files to upload


## Ingesting through the API

Ingesting a dataset or model through the API is a multi step (and error prone) process:

1. Create/Retrieve a dataset
2. Create a version
3. Ingest files to version
	1. Ingest small files in batches
	2. Ingest large files in chunks as multipart upload
		1. Create multipart upload
		2. Ingest chunks
		3. Complete multipart upload
	3. Ingest existing files in batches to new version

The library/CLI will take care of these steps, so it is the recommended way to ingest a dataset. 

However, if you still want to ingest datasets with the API, we recommend following the previous steps using the API [documentation](https://api.eotdl.com/docs) or reading the implementation of the ingestion functions in the library. If you need further help, reach out to us at the Discord server.

This is a process we would like to simplify in the future.
