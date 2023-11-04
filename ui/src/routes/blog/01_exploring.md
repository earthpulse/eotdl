---
title: Exploring and downloading Datasets and Models
date: '2023-11-04T01:00:00.000Z'
description: In this post you will learn how to explore and download the datasets and models hosted on EOTDL with the different tools of the environment
tags: getting started, explore, download, datasets, models
link: https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/01_exploring.ipynb
---

# Exploring and Downloading Datasets and Models

Let's start by exploring the repository of datasets and models. 

You can do that at the different accessibility layers of EOTDL: the user interface, the API, the command line interface (CLI) and the Python library.

## The User Interface

The easiest way to get started with EOTDL is by exploring the user interface: [https://eotdl.com/](https://www.eotdl.com/). Through the UI you will be able to:

- Explore the datasets and models available in the repository (filtering by name, tags and liked)
- Edit your own datasets and models information.
- Read the tutorials on the blog.
- Read the documentation.
- Find useful links to other resources (GitHub, Discord, ...)

## Quality levels

Datasets and models in EOTDL are categorized into quality levels. The quality levels are:

- **Q0**: datasets in the form of an archive with arbitary files without curation. This level is ideal for easy and fast upload/download of small datasets.
- **Q1**: datasets with STAC metadata but no QA. These datasets can leverage a limited set of EOTDL features.
- **Q2**: datasets with STAC metadata with the EOTDL custom extensions and automated QA. These datasets can leverage the full potential of the EOTDL.
- **Q3**: Q2 datasets that are manually curated. These datasets are the most reliable and can be used as benchmark datasets.


## The Command Line Interface

Even though the UI is the easiest way to get started, it is not the most convenient for actually working with the datasets and models. For that we recommend installing the CLI.

If you are running this notebook locally, consider creating a virtual environment before installing the CLI to avoid conflicts with other packages.

With conda:

```bash
conda create -n eotdl python=3.8
conda activate eotdl
```

With python: 

```bash
python -m venv eotdl
source eotdl/bin/activate
```

You may also have to install Jupyter on the new environment and restart the notebook.

Then, you can install the CLI with pip:


```python
# uncomment to install

# !pip install eotdl
```

Once installed, you can execute the CLI with different commands. 


```python
!eotdl --help
```

    [1m                                                                                [0m
    [1m [0m[1;33mUsage: [0m[1meotdl [OPTIONS] COMMAND [ARGS]...[0m[1m                                      [0m[1m [0m
    [1m                                                                                [0m
     Welcome to EOTDL. Learn more at https://www.eotdl.com/                         
                                                                                    
    [2m╭─[0m[2m Options [0m[2m───────────────────────────────────────────────────────────────────[0m[2m─╮[0m
    [2m│[0m [1;36m-[0m[1;36m-install[0m[1;36m-completion[0m          Install completion for the current shell.      [2m│[0m
    [2m│[0m [1;36m-[0m[1;36m-show[0m[1;36m-completion[0m             Show completion for the current shell, to copy [2m│[0m
    [2m│[0m                               it or customize the installation.              [2m│[0m
    [2m│[0m [1;36m-[0m[1;36m-help[0m                        Show this message and exit.                    [2m│[0m
    [2m╰──────────────────────────────────────────────────────────────────────────────╯[0m
    [2m╭─[0m[2m Commands [0m[2m──────────────────────────────────────────────────────────────────[0m[2m─╮[0m
    [2m│[0m [1;36mauth       [0m[1;36m [0m Login to EOTDL.                                                 [2m│[0m
    [2m│[0m [1;36mdatasets   [0m[1;36m [0m Explore, ingest and download training datasets.                 [2m│[0m
    [2m│[0m [1;36mmodels     [0m[1;36m [0m Explore, ingest and download ML models.                         [2m│[0m
    [2m│[0m [1;36mversion    [0m[1;36m [0m Get EOTDL version.                                              [2m│[0m
    [2m╰──────────────────────────────────────────────────────────────────────────────╯[0m
    



```python
!eotdl version
```

    EOTDL Version: 2023.11.02-5



```python
!eotdl datasets --help
```

    [1m                                                                                [0m
    [1m [0m[1;33mUsage: [0m[1meotdl datasets [OPTIONS] COMMAND [ARGS]...[0m[1m                             [0m[1m [0m
    [1m                                                                                [0m
     Explore, ingest and download training datasets.                                
                                                                                    
    [2m╭─[0m[2m Options [0m[2m───────────────────────────────────────────────────────────────────[0m[2m─╮[0m
    [2m│[0m [1;36m-[0m[1;36m-help[0m          Show this message and exit.                                  [2m│[0m
    [2m╰──────────────────────────────────────────────────────────────────────────────╯[0m
    [2m╭─[0m[2m Commands [0m[2m──────────────────────────────────────────────────────────────────[0m[2m─╮[0m
    [2m│[0m [1;36mget      [0m[1;36m [0m Download a dataset from the EOTDL.                                [2m│[0m
    [2m│[0m [1;36mingest   [0m[1;36m [0m Ingest a dataset to the EOTDL.                                    [2m│[0m
    [2m│[0m [1;36mlist     [0m[1;36m [0m Retrieve a list with all the datasets in the EOTDL.               [2m│[0m
    [2m╰──────────────────────────────────────────────────────────────────────────────╯[0m
    


You can explore datasets with the following command:


```python
!eotdl datasets list 
```

    ['EuroSAT-RGB', 'UCMerced', 'EuroSAT', 'SeCo100k', 'SeCo', 'AirbusAircraftDetection', 'AirbusWindTurbinesPatches', 'RoadNet', 'SloveniaLandCover', 'ISPRS-Potsdam2D', 'SEN12-FLOOD', 'Urban3dChallenge', 'tropical-cyclone-dataset', 'Vessel-detection', 'Airplanes-detection', 'S2-SHIPS', 'SpaceNet-7', 'Sentinel-2-Cloud-Mask', 'PASTIS', 'FlodNet', 'EuroCrops', 'open-cities-test', 'PASTIS-R', 'open-cities-tt1-source', 'open-cities-tt2-source', 'LandcoverAI', 'xview2', 'BigEarthNet', 'EuroSAT-RGB-STAC', 'EuroSAT-STAC', 'COWC', 'Stanford-Drone-dataset', 'eurosat-rgb', 'eurosat-rgb-q2', 'EuroSAT-small', 'test-q0', 'Boadella-BiDS23']



```python
!eotdl datasets list --help
```

    [1m                                                                                [0m
    [1m [0m[1;33mUsage: [0m[1meotdl datasets list [OPTIONS][0m[1m                                          [0m[1m [0m
    [1m                                                                                [0m
     Retrieve a list with all the datasets in the EOTDL.                            
     [2mIf using [0m[1;2;36m-[0m[1;2;36m-name[0m[2m, it will filter the results by name. If no name is provided, [0m  
     [2mit will return all the datasets.[0m                                               
     [2mIf using [0m[1;2;36m-[0m[1;2;36m-limit[0m[2m, it will limit the number of results. If no limit is [0m         
     [2mprovided, it will return all the datasets.[0m                                     
                                                                                    
     [2mExamples[0m                                                                       
     [1;2;36m--------[0m                                                                       
     [2m$ eotdl datasets list[0m                                                          
     [2m$ eotdl datasets list [0m[1;2;36m-[0m[1;2;36m-name[0m[2m YourModel [0m[1;2;36m-[0m[1;2;36m-limit[0m[2m 5[0m                               
                                                                                    
    [2m╭─[0m[2m Options [0m[2m───────────────────────────────────────────────────────────────────[0m[2m─╮[0m
    [2m│[0m [1;36m-[0m[1;36m-name[0m   [1;32m-n[0m      [1;33mTEXT   [0m  Filter the returned datasets by name               [2m│[0m
    [2m│[0m                           [2m[default: None]                     [0m               [2m│[0m
    [2m│[0m [1;36m-[0m[1;36m-limit[0m  [1;32m-l[0m      [1;33mINTEGER[0m  Limit the number of returned results               [2m│[0m
    [2m│[0m                           [2m[default: None]                     [0m               [2m│[0m
    [2m│[0m [1;36m-[0m[1;36m-help[0m           [1;33m       [0m  Show this message and exit.                        [2m│[0m
    [2m╰──────────────────────────────────────────────────────────────────────────────╯[0m
    



```python
!eotdl datasets list -n eurosat
```

    ['EuroSAT-RGB', 'EuroSAT', 'EuroSAT-RGB-STAC', 'EuroSAT-STAC', 'eurosat-rgb', 'eurosat-rgb-q2', 'EuroSAT-small']


As you may have guessed, you can download a dataset with the following command:


```python
!eotdl datasets get EuroSAT-small
```

    Dataset `EuroSAT-small v10` already exists at /home/juan/.cache/eotdl/datasets/EuroSAT-small/v10. To force download, use force=True or -f in the CLI.


The first time you run the command, you will be asked to login (which will require you to create an account if you haven't already). You can also login with the command


```python
!eotdl auth login
```

    You are logged in as it@earthpulse.es



```python
!eotdl auth --help
```

    [1m                                                                                [0m
    [1m [0m[1;33mUsage: [0m[1meotdl auth [OPTIONS] COMMAND [ARGS]...[0m[1m                                 [0m[1m [0m
    [1m                                                                                [0m
     Login to EOTDL.                                                                
                                                                                    
    [2m╭─[0m[2m Options [0m[2m───────────────────────────────────────────────────────────────────[0m[2m─╮[0m
    [2m│[0m [1;36m-[0m[1;36m-help[0m          Show this message and exit.                                  [2m│[0m
    [2m╰──────────────────────────────────────────────────────────────────────────────╯[0m
    [2m╭─[0m[2m Commands [0m[2m──────────────────────────────────────────────────────────────────[0m[2m─╮[0m
    [2m│[0m [1;36mlogin            [0m[1;36m [0m Login to the EOTDL.                                       [2m│[0m
    [2m│[0m [1;36mlogout           [0m[1;36m [0m Logout from the EOTDL.                                    [2m│[0m
    [2m╰──────────────────────────────────────────────────────────────────────────────╯[0m
    



```python
!eotdl datasets get --help
```

    [1m                                                                                [0m
    [1m [0m[1;33mUsage: [0m[1meotdl datasets get [OPTIONS] [DATASET][0m[1m                                 [0m[1m [0m
    [1m                                                                                [0m
     Download a dataset from the EOTDL.                                             
     [2mIf using [0m[1;2;36m-[0m[1;2;36m-path[0m[2m, it will download the dataset to the specified path. If no [0m    
     [2mpath is provided, it will download to ~/.eotdl/datasets.[0m                       
     [2mIf using [0m[1;2;36m-[0m[1;2;36m-file[0m[2m, it will download the specified file. If no file is provided, [0m 
     [2mit will download the entire dataset.[0m                                           
     [2mIf using [0m[1;2;36m-[0m[1;2;36m-version[0m[2m, it will download the specified version. If no version is [0m  
     [2mprovided, it will download the latest version.[0m                                 
     [2mIf using [0m[1;2;36m-[0m[1;2;36m-assets[0m[2m when the dataset is STAC, it will also download the STAC [0m    
     [2massets of the dataset. If not provided, it will only download the STAC [0m        
     [2mmetadata.[0m                                                                      
     [2mIf using [0m[1;2;36m-[0m[1;2;36m-force[0m[2m, it will download the dataset even if the file already [0m       
     [2mexists.[0m                                                                        
     [2mIf using [0m[1;2;36m-[0m[1;2;36m-verbose[0m[2m, it will print the progress of the download.[0m                
                                                                                    
     [2mExamples[0m                                                                       
     [1;2;36m--------[0m                                                                       
     [2m$ eotdl dataset get YourDataset[0m                                                
     [2m$ eotdl dataset get YourDataset [0m[1;2;36m-[0m[1;2;36m-path[0m[2m /path/to/download [0m[1;2;36m-[0m[1;2;36m-file[0m[2m dataset.zip [0m   
     [1;2;36m-[0m[1;2;36m-version[0m[2m 1 [0m[1;2;36m-[0m[1;2;36m-assets[0m[2m True [0m[1;2;36m-[0m[1;2;36m-force[0m[2m True [0m[1;2;36m-[0m[1;2;36m-verbose[0m[2m True[0m                          
                                                                                    
    [2m╭─[0m[2m Arguments [0m[2m─────────────────────────────────────────────────────────────────[0m[2m─╮[0m
    [2m│[0m   dataset      [1;2;33m[[0m[1;33mDATASET[0m[1;2;33m][0m  Name of the dataset to download [2m[default: None][0m    [2m│[0m
    [2m╰──────────────────────────────────────────────────────────────────────────────╯[0m
    [2m╭─[0m[2m Options [0m[2m───────────────────────────────────────────────────────────────────[0m[2m─╮[0m
    [2m│[0m [1;36m-[0m[1;36m-path[0m     [1;32m-p[0m      [1;33mTEXT   [0m  Download the dataset to a specific output path   [2m│[0m
    [2m│[0m                             [2m[default: None]                               [0m   [2m│[0m
    [2m│[0m [1;36m-[0m[1;36m-file[0m     [1;32m-f[0m      [1;33mTEXT   [0m  Download a specific file from the dataset        [2m│[0m
    [2m│[0m                             [2m[default: None]                          [0m        [2m│[0m
    [2m│[0m [1;36m-[0m[1;36m-version[0m  [1;32m-v[0m      [1;33mINTEGER[0m  Dataset version [2m[default: None][0m                  [2m│[0m
    [2m│[0m [1;36m-[0m[1;36m-assets[0m   [1;32m-a[0m      [1;33m       [0m  Download STAC assets from the dataset            [2m│[0m
    [2m│[0m [1;36m-[0m[1;36m-force[0m    [1;32m-f[0m      [1;33m       [0m  Force download even if file exists               [2m│[0m
    [2m│[0m [1;36m-[0m[1;36m-verbose[0m          [1;33m       [0m  Verbose output. This will print the progress of  [2m│[0m
    [2m│[0m                             the download                                     [2m│[0m
    [2m│[0m [1;36m-[0m[1;36m-help[0m             [1;33m       [0m  Show this message and exit.                      [2m│[0m
    [2m╰──────────────────────────────────────────────────────────────────────────────╯[0m
    


By default, datasets will be downloaded to your `$HOME/.cache/eotdl/datasets` folder or the path in the `EOTDL_DOWNLOAD_PATH` environment variable. You can change this with the `--path` argument.


```python
!eotdl datasets get EuroSAT-small -p data
```

    Dataset `EuroSAT-small v10` already exists at data/EuroSAT-small/v10. To force download, use force=True or -f in the CLI.


You can choose a particular version to download with the `--version` argument. If you don't specify a version, the latest version will be downloaded.


```python
!eotdl datasets get EuroSAT-small -p data -v 1
```

    100%|███████████████████████████████████████████| 6/6 [00:02<00:00,  2.35file/s]
    Data available at data/EuroSAT-small/v1


The version number will be used to create a folder with the same name inside the path you specified. Inside this folder you will find the dataset files.

If you try to re-download a datasets, the CLI will complain. You can force a re-download with the `--force` argument.


```python
!eotdl datasets get EuroSAT-small -p data -v 1
```

    Dataset `EuroSAT-small v1` already exists at data/EuroSAT-small/v1. To force download, use force=True or -f in the CLI.



```python
!eotdl datasets get EuroSAT-small -p data -v 1 -f
```

    100%|███████████████████████████████████████████| 6/6 [00:02<00:00,  2.39file/s]
    Data available at data/EuroSAT-small/v1


For Q1+ datasets, the `get` command will only download the STAC metadata of the dataset.


```python
!eotdl datasets get eurosat-rgb -p data 
```

    Downloading a STAC dataset is not implemented


Inside the metadata you will find the links to all the assets, so you can download them individually (maybe after some filtering or processing using only the metadata). However, you can download all assets with the command:


```python
!eotdl datasets get eurosat-rgb -p data -a
```

    Downloading a STAC dataset is not implemented


Working with models is very much the same at this point.


```python
!eotdl models --help
```

    [1m                                                                                [0m
    [1m [0m[1;33mUsage: [0m[1meotdl models [OPTIONS] COMMAND [ARGS]...[0m[1m                               [0m[1m [0m
    [1m                                                                                [0m
     Explore, ingest and download ML models.                                        
                                                                                    
    [2m╭─[0m[2m Options [0m[2m───────────────────────────────────────────────────────────────────[0m[2m─╮[0m
    [2m│[0m [1;36m-[0m[1;36m-help[0m          Show this message and exit.                                  [2m│[0m
    [2m╰──────────────────────────────────────────────────────────────────────────────╯[0m
    [2m╭─[0m[2m Commands [0m[2m──────────────────────────────────────────────────────────────────[0m[2m─╮[0m
    [2m│[0m [1;36mget      [0m[1;36m [0m Download a model from the EOTDL.                                  [2m│[0m
    [2m│[0m [1;36mingest   [0m[1;36m [0m Ingest a model to the EOTDL.                                      [2m│[0m
    [2m│[0m [1;36mlist     [0m[1;36m [0m Retrieve a list with all the models in the EOTDL.                 [2m│[0m
    [2m╰──────────────────────────────────────────────────────────────────────────────╯[0m
    



```python
!eotdl models list
```

    ['EuroSAT-RGB-BiDS23']



```python
!eotdl models list --help
```

    [1m                                                                                [0m
    [1m [0m[1;33mUsage: [0m[1meotdl models list [OPTIONS][0m[1m                                            [0m[1m [0m
    [1m                                                                                [0m
     Retrieve a list with all the models in the EOTDL.                              
     [2mIf using [0m[1;2;36m-[0m[1;2;36m-name[0m[2m, it will filter the results by name. If no name is provided, [0m  
     [2mit will return all the models.[0m                                                 
     [2mIf using [0m[1;2;36m-[0m[1;2;36m-limit[0m[2m, it will limit the number of results. If no limit is [0m         
     [2mprovided, it will return all the models.[0m                                       
                                                                                    
     [2mExamples[0m                                                                       
     [1;2;36m--------[0m                                                                       
     [2m$ eotdl models list[0m                                                            
     [2m$ eotdl models list [0m[1;2;36m-[0m[1;2;36m-name[0m[2m YourModel [0m[1;2;36m-[0m[1;2;36m-limit[0m[2m 5[0m                                 
                                                                                    
    [2m╭─[0m[2m Options [0m[2m───────────────────────────────────────────────────────────────────[0m[2m─╮[0m
    [2m│[0m [1;36m-[0m[1;36m-name[0m   [1;32m-n[0m      [1;33mTEXT   [0m  Filter the returned models by name [2m[default: None][0m [2m│[0m
    [2m│[0m [1;36m-[0m[1;36m-limit[0m  [1;32m-l[0m      [1;33mINTEGER[0m  Limit the number of returned results               [2m│[0m
    [2m│[0m                           [2m[default: None]                     [0m               [2m│[0m
    [2m│[0m [1;36m-[0m[1;36m-help[0m           [1;33m       [0m  Show this message and exit.                        [2m│[0m
    [2m╰──────────────────────────────────────────────────────────────────────────────╯[0m
    



```python
!eotdl models get EuroSAT-RGB-BiDS23
```

    100%|███████████████████████████████████████████| 2/2 [00:05<00:00,  2.54s/file]
    Data available at /home/juan/.cache/eotdl/models/EuroSAT-RGB-BiDS23/v3



```python
!eotdl models get --help
```

    [1m                                                                                [0m
    [1m [0m[1;33mUsage: [0m[1meotdl models get [OPTIONS] [MODEL][0m[1m                                     [0m[1m [0m
    [1m                                                                                [0m
     Download a model from the EOTDL.                                               
     [2mIf using [0m[1;2;36m-[0m[1;2;36m-path[0m[2m, it will download the model to the specified path. If no path [0m 
     [2mis provided, it will download to ~/.eotdl/models.[0m                              
     [2mIf using [0m[1;2;36m-[0m[1;2;36m-file[0m[2m, it will download the specified file. If no file is provided, [0m 
     [2mit will download the entire model.[0m                                             
     [2mIf using [0m[1;2;36m-[0m[1;2;36m-version[0m[2m, it will download the specified version. If no version is [0m  
     [2mprovided, it will download the latest version.[0m                                 
     [2mIf using [0m[1;2;36m-[0m[1;2;36m-assets[0m[2m when the model is STAC, it will also download the STAC [0m      
     [2massets of the model. If not provided, it will only download the STAC metadata.[0m 
     [2mIf using [0m[1;2;36m-[0m[1;2;36m-force[0m[2m, it will download the model even if the file already exists.[0m  
     [2mIf using [0m[1;2;36m-[0m[1;2;36m-verbose[0m[2m, it will print the progress of the download.[0m                
                                                                                    
     [2mExamples[0m                                                                       
     [1;2;36m--------[0m                                                                       
     [2m$ eotdl models get YourModel[0m                                                   
     [2m$ eotdl models get YourModel [0m[1;2;36m-[0m[1;2;36m-path[0m[2m /path/to/download [0m[1;2;36m-[0m[1;2;36m-file[0m[2m model.zip [0m        
     [1;2;36m-[0m[1;2;36m-version[0m[2m 1 [0m[1;2;36m-[0m[1;2;36m-assets[0m[2m True [0m[1;2;36m-[0m[1;2;36m-force[0m[2m True [0m[1;2;36m-[0m[1;2;36m-verbose[0m[2m True[0m                          
                                                                                    
    [2m╭─[0m[2m Arguments [0m[2m─────────────────────────────────────────────────────────────────[0m[2m─╮[0m
    [2m│[0m   model      [1;2;33m[[0m[1;33mMODEL[0m[1;2;33m][0m  Name of the model to download [2m[default: None][0m          [2m│[0m
    [2m╰──────────────────────────────────────────────────────────────────────────────╯[0m
    [2m╭─[0m[2m Options [0m[2m───────────────────────────────────────────────────────────────────[0m[2m─╮[0m
    [2m│[0m [1;36m-[0m[1;36m-path[0m     [1;32m-p[0m      [1;33mTEXT   [0m  Download the model to a specific output path     [2m│[0m
    [2m│[0m                             [2m[default: None]                             [0m     [2m│[0m
    [2m│[0m [1;36m-[0m[1;36m-file[0m     [1;32m-f[0m      [1;33mTEXT   [0m  Download a specific file from the model          [2m│[0m
    [2m│[0m                             [2m[default: None]                        [0m          [2m│[0m
    [2m│[0m [1;36m-[0m[1;36m-version[0m  [1;32m-v[0m      [1;33mINTEGER[0m  Model version [2m[default: None][0m                    [2m│[0m
    [2m│[0m [1;36m-[0m[1;36m-assets[0m   [1;32m-a[0m      [1;33m       [0m  Download STAC assets from the model              [2m│[0m
    [2m│[0m [1;36m-[0m[1;36m-force[0m    [1;32m-f[0m      [1;33m       [0m  Force download even if file exists               [2m│[0m
    [2m│[0m [1;36m-[0m[1;36m-verbose[0m          [1;33m       [0m  Verbose output. This will print the progress of  [2m│[0m
    [2m│[0m                             the download                                     [2m│[0m
    [2m│[0m [1;36m-[0m[1;36m-help[0m             [1;33m       [0m  Show this message and exit.                      [2m│[0m
    [2m╰──────────────────────────────────────────────────────────────────────────────╯[0m
    


We will explore how to ingest datasets and models in the next tutorials.

## The Library

Everything that we have done so far with the CLI is also enabled through the Python library. When installing the CLI, the library is automatically installed as well.


```python
import eotdl

eotdl.__version__
```




    '2023.11.02-5'




```python
from eotdl.datasets import retrieve_datasets

datasets = retrieve_datasets()
len(datasets)
```




    37




```python
retrieve_datasets("eurosat")
```




    ['EuroSAT-RGB',
     'EuroSAT',
     'EuroSAT-RGB-STAC',
     'EuroSAT-STAC',
     'eurosat-rgb',
     'eurosat-rgb-q2',
     'EuroSAT-small']



With the library, you have full control over the datasets and models.


```python
[d for d in datasets if "eurosat" in d.lower()]
```




    ['EuroSAT-RGB',
     'EuroSAT',
     'EuroSAT-RGB-STAC',
     'EuroSAT-STAC',
     'eurosat-rgb',
     'eurosat-rgb-q2',
     'EuroSAT-small']



You can download datasets as well, but now you will have to manage potential errors.


```python
from eotdl.datasets import download_dataset

download_dataset("EuroSAT-small")
```


    ---------------------------------------------------------------------------

    Exception                                 Traceback (most recent call last)

    /home/juan/Desktop/eotdl/tutorials/notebooks/01_exploring.ipynb Cell 50 line 3
          <a href='vscode-notebook-cell://ssh-remote%2Bharley/home/juan/Desktop/eotdl/tutorials/notebooks/01_exploring.ipynb#Y100sdnNjb2RlLXJlbW90ZQ%3D%3D?line=0'>1</a> from eotdl.datasets import download_dataset
    ----> <a href='vscode-notebook-cell://ssh-remote%2Bharley/home/juan/Desktop/eotdl/tutorials/notebooks/01_exploring.ipynb#Y100sdnNjb2RlLXJlbW90ZQ%3D%3D?line=2'>3</a> download_dataset("EuroSAT-small")


    File ~/miniconda3/envs/eotdl/lib/python3.8/site-packages/eotdl/auth/auth.py:47, in with_auth.<locals>.wrapper(*args, **kwargs)
         45 def wrapper(*args, **kwargs):
         46     user = auth()
    ---> 47     return func(*args, **kwargs, user=user)


    File ~/miniconda3/envs/eotdl/lib/python3.8/site-packages/eotdl/datasets/download.py:42, in download_dataset(dataset_name, version, path, logger, assets, force, verbose, user, file)
         40 if os.path.exists(download_path) and not force:
         41     os.makedirs(download_path, exist_ok=True)
    ---> 42     raise Exception(
         43         f"Dataset `{dataset['name']} v{str(version)}` already exists at {download_path}. To force download, use force=True or -f in the CLI."
         44     )
         45 if dataset["quality"] == 0:
         46     if file:


    Exception: Dataset `EuroSAT-small v10` already exists at /home/juan/.cache/eotdl/datasets/EuroSAT-small/v10. To force download, use force=True or -f in the CLI.



```python
download_dataset("EuroSAT-small", force=True)
```

    100%|██████████| 7/7 [00:02<00:00,  2.57file/s]





    '/home/juan/.cache/eotdl/datasets/EuroSAT-small/v10'




```python
download_dataset("EuroSAT-small", force=True, path="data")
```

    100%|██████████| 7/7 [00:02<00:00,  2.76file/s]





    'data/EuroSAT-small/v10'



In fact, the CLI is built on top of the library.

And the same for the models


```python
from eotdl.models import retrieve_models

retrieve_models()
```




    ['EuroSAT-RGB-BiDS23']




```python
from eotdl.models import download_model 

path = download_model("EuroSAT-RGB-BiDS23", force=True)
path
```

    100%|██████████| 2/2 [00:04<00:00,  2.26s/file]





    '/home/juan/.cache/eotdl/models/EuroSAT-RGB-BiDS23/v3'




```python
import os 

os.listdir(path)
```




    ['metadata.yml', 'model.onnx']



## The Application Programming Interface

The last way to interact with EOTDL is using the API. You can explore the interactive documentation at [https://api.eotdl.com/docs](https://api.eotdl.com/docs)

You can get the full list of datasets hosted in the EOTDL with the followgin API call:


```python
import requests

datasets = requests.get("https://api.eotdl.com/datasets").json()
datasets
```




    [{'uid': 'auth0|616b0057af0c7500691a026e',
      'id': '6454b4ba05740a8762edfcdb',
      'name': 'EuroSAT-RGB',
      'authors': [' Patrick Helber'],
      'source': 'http://madm.dfki.de/downloads',
      'license': '-',
      'files': '6526972d7d4d50bd035d033d',
      'versions': [{'version_id': 1,
        'createdAt': '2023-10-11T14:37:38.155',
        'size': 377122268},
       {'version_id': 2, 'createdAt': '2023-10-11T15:38:45.833', 'size': 0},
       {'version_id': 3, 'createdAt': '2023-10-11T15:38:45.833', 'size': 0},
       {'version_id': 4, 'createdAt': '2023-10-11T15:38:45.833', 'size': 0},
       {'version_id': 5, 'createdAt': '2023-10-11T15:38:45.833', 'size': 0},
       {'version_id': 6, 'createdAt': '2023-10-11T15:38:45.833', 'size': 0},
       {'version_id': 7, 'createdAt': '2023-10-11T15:38:45.833', 'size': 0},
       {'version_id': 8, 'createdAt': '2023-10-12T07:14:16.642', 'size': 5406191},
       {'version_id': 9, 'createdAt': '2023-10-12T07:14:16.642', 'size': 5610422},
       {'version_id': 10,
        'createdAt': '2023-10-12T07:14:16.642',
        'size': 13106283},
       {'version_id': 11,
        'createdAt': '2023-10-12T07:14:16.642',
        'size': 13031233},
       {'version_id': 12,
        'createdAt': '2023-10-12T07:14:16.642',
        'size': 15113295},
       {'version_id': 13,
        'createdAt': '2023-10-12T07:14:16.642',
        'size': 13494311}],
      'description': '<p><strong>EuroSAT: A land use and land cover classification dataset based on Sentinel-2 satellite images.</strong></p><p><br></p><p>This is the RGB version of <a href="https://www.eotdl.com/datasets/EuroSAT" rel="noopener noreferrer" target="_blank">EuroSAT</a>.</p><p><br></p><p><a href="https://arxiv.org/abs/1709.00029" rel="noopener noreferrer" target="_blank">Paper</a></p><p><a href="http://madm.dfki.de/downloads" rel="noopener noreferrer" target="_blank">Alternative download link</a></p><p><br></p><p><span style="color: rgb(0, 0, 0);">Land use and land cover classification using Sentinel-2 satellite images. </span></p><p><br></p><p><span style="color: rgb(0, 0, 0);">The Sentinel-2 satellite images are openly and freely accessible provided in the Earth observation program Copernicus. We present a novel dataset based on Sentinel-2 satellite images covering 13 spectral bands and consisting out of 10 classes with in total 27,000 labeled and geo-referenced images. </span></p><p><br></p><p><br></p>',
      'tags': ['image classification', 'land cover', 'land use', 'sentinel-2'],
      'createdAt': '2023-05-03T15:46:15.491',
      'updatedAt': '2023-10-25T16:19:16.611',
      'likes': 1,
      'downloads': 40,
      'quality': 0},
     {'uid': 'auth0|616b0057af0c7500691a026e',
      'id': '645a26564d1c8b7b364ee631',
      'name': 'UCMerced',
      'authors': ['Yi Yang and Shawn Newsam'],
      'source': 'http://weegee.vision.ucmerced.edu/datasets/landuse.html',
      'license': '-',
      'files': '6526972d7d4d50bd035d033e',
      'versions': [{'version_id': 1,
        'createdAt': '2023-10-11T14:37:38.155',
        'size': 94280567}],
      'description': '<h1>UC Merced Land Use Dataset</h1><p>*info extracted from the <a href="http://weegee.vision.ucmerced.edu/datasets/landuse.html" rel="noopener noreferrer" target="_blank">official page</a>.</p><p><br></p><p>This is a 21 class land use image dataset meant for research purposes.</p><p>There are 100 images for each of the following classes:</p><ul><li>agricultural</li><li>airplane</li><li>baseballdiamond</li><li>beach</li><li>buildings</li><li>chaparral</li><li>denseresidential</li><li>forest</li><li>freeway</li><li>golfcourse</li><li>harbor</li><li>intersection</li><li>mediumresidential</li><li>mobilehomepark</li><li>overpass</li><li>parkinglot</li><li>river</li><li>runway</li><li>sparseresidential</li><li>storagetanks</li><li>tenniscourt</li></ul><p>Each image measures 256x256 pixels.</p><p><br></p><p>The images were manually extracted from large images from the USGS National Map Urban Area Imagery collection for various urban areas around the country. The pixel resolution of this public domain imagery is 1 foot.</p><p><br></p><p>Please cite the following paper when publishing results that use this dataset:</p><p><br></p><p><em>Yi Yang and Shawn Newsam, "Bag-Of-Visual-Words and Spatial Extensions for Land-Use Classification," ACM SIGSPATIAL International Conference on Advances in Geographic Information Systems (ACM GIS), 2010.</em></p><p><br></p><p>Shawn D. Newsam</p><p>Assistant Professor and Founding Faculty</p><p>Electrical Engineering &amp; Computer Science</p><p>University of California, Merced</p><p><br></p><p>Email: snewsam@ucmerced.edu</p><p><br></p><p>Web: http://faculty.ucmerced.edu/snewsam</p><p><br></p><p>This material is based upon work supported by the National Science Foundation under Grant No.&nbsp;<a href="http://nsf.gov/awardsearch/showAward.do?AwardNumber=0917069" rel="noopener noreferrer" target="_blank">0917069</a>.</p>',
      'tags': ['sentinel-2', 'land use', 'image classification'],
      'createdAt': '2023-05-09T10:52:06.487',
      'updatedAt': '2023-06-08T17:30:07.36',
      'likes': 1,
      'downloads': 9,
      'quality': 0},
     {'uid': 'auth0|616b0057af0c7500691a026e',
      'id': '645d1e4ec3060c653291ce87',
      'name': 'EuroSAT',
      'authors': [' Patrick Helber'],
      'source': 'http://madm.dfki.de/downloads',
      'license': '-',
      'files': '652697317d4d50bd035d033f',
      'versions': [{'version_id': 1,
        'createdAt': '2023-10-11T14:37:38.155',
        'size': 2067725275}],
      'description': '<h1><strong style="color: rgb(31, 41, 55);">EuroSAT: A land use and land cover classification dataset based on Sentinel-2 satellite images.</strong></h1><p><br></p><p><a href="https://arxiv.org/abs/1709.00029" rel="noopener noreferrer" target="_blank">Paper</a></p><p><br></p><p><span style="color: rgb(0, 0, 0);">Land use and land cover classification using Sentinel-2 satellite images. </span></p><p><br></p><p><span style="color: rgb(0, 0, 0);">The Sentinel-2 satellite images are openly and freely accessible provided in the Earth observation program Copernicus. We present a novel dataset based on Sentinel-2 satellite images covering 13 spectral bands and consisting out of 10 classes with in total 27,000 labeled and geo-referenced images. </span></p>',
      'tags': ['land cover', 'land use', 'sentinel-2', 'image classification'],
      'createdAt': '2023-05-11T18:10:15.405',
      'updatedAt': '2023-05-23T18:00:20.776',
      'likes': 1,
      'downloads': 13,
      'quality': 0},
     {'uid': 'auth0|616b0057af0c7500691a026e',
      'id': '645dff70c2f02fdd88c47b67',
      'name': 'SeCo100k',
      'authors': ['ServiceNow'],
      'source': 'https://github.com/ServiceNow/seasonal-contrast',
      'license': '-',
      'files': '6526973d7d4d50bd035d0340',
      'versions': [{'version_id': 1,
        'createdAt': '2023-10-11T14:37:38.155',
        'size': 7302001636}],
      'description': '<h1>Seasonal Contrast: Unsupervised Pre-Training from Uncurated Remote Sensing Data</h1><p><br></p><p>This is the small version of <a href="https://www.eotdl.com/datasets/SeCo" rel="noopener noreferrer" target="_blank">SeCo</a>.</p><p><br></p><p><a href="https://arxiv.org/abs/2103.16607" rel="noopener noreferrer" target="_blank">Paper</a></p><p><a href="https://github.com/ServiceNow/seasonal-contrast" rel="noopener noreferrer" target="_blank">Github</a></p><p><br></p><p><span style="color: rgb(0, 0, 0);">Remote sensing and automatic earth monitoring are key to solve global-scale challenges such as disaster prevention, land use monitoring, or tackling climate change. Although there exist vast amounts of remote sensing data, most of it remains unlabeled and thus inaccessible for supervised learning algorithms. Transfer learning approaches can reduce the data requirements of deep learning algorithms. However, most of these methods are pre-trained on ImageNet and their generalization to remote sensing imagery is not guaranteed due to the domain gap. In this work, we propose Seasonal Contrast (SeCo), an effective pipeline to leverage unlabeled data for in-domain pre-training of remote sensing representations. The SeCo pipeline is composed of two parts. First, a principled procedure to gather large-scale, unlabeled and uncurated remote sensing datasets containing images from multiple Earth locations at different timestamps. Second, a self-supervised algorithm that takes advantage of time and position invariance to learn transferable representations for remote sensing applications. We empirically show that models trained with SeCo achieve better performance than their ImageNet pre-trained counterparts and state-of-the-art self-supervised learning methods on multiple downstream tasks. The datasets and models in SeCo will be made public to facilitate transfer learning and enable rapid progress in remote sensing applications.</span></p>',
      'tags': ['unsupervised learning', 'sentinel-2'],
      'createdAt': '2023-05-11T19:15:20.586',
      'updatedAt': '2023-05-23T18:02:08.795',
      'likes': 1,
      'downloads': 2,
      'quality': 0},
     {'uid': 'auth0|616b0057af0c7500691a026e',
      'id': '645e0fb2c2f02fdd88c47b70',
      'name': 'SeCo',
      'authors': ['ServiceNow'],
      'source': 'https://github.com/ServiceNow/seasonal-contrast',
      'license': '-',
      'files': '6526977c7d4d50bd035d0341',
      'versions': [{'version_id': 1,
        'createdAt': '2023-10-11T14:37:38.155',
        'size': 36325857720}],
      'description': '<h1>Seasonal Contrast: Unsupervised Pre-Training from Uncurated Remote Sensing Data</h1><p><br></p><p><a href="https://arxiv.org/abs/2103.16607" rel="noopener noreferrer" target="_blank">Paper</a></p><p><a href="https://github.com/ServiceNow/seasonal-contrast" rel="noopener noreferrer" target="_blank">Github</a></p><p><br></p><p><span style="color: rgb(0, 0, 0);">Remote sensing and automatic earth monitoring are key to solve global-scale challenges such as disaster prevention, land use monitoring, or tackling climate change. Although there exist vast amounts of remote sensing data, most of it remains unlabeled and thus inaccessible for supervised learning algorithms. Transfer learning approaches can reduce the data requirements of deep learning algorithms. However, most of these methods are pre-trained on ImageNet and their generalization to remote sensing imagery is not guaranteed due to the domain gap. In this work, we propose Seasonal Contrast (SeCo), an effective pipeline to leverage unlabeled data for in-domain pre-training of remote sensing representations. The SeCo pipeline is composed of two parts. First, a principled procedure to gather large-scale, unlabeled and uncurated remote sensing datasets containing images from multiple Earth locations at different timestamps. Second, a self-supervised algorithm that takes advantage of time and position invariance to learn transferable representations for remote sensing applications. We empirically show that models trained with SeCo achieve better performance than their ImageNet pre-trained counterparts and state-of-the-art self-supervised learning methods on multiple downstream tasks. The datasets and models in SeCo will be made public to facilitate transfer learning and enable rapid progress in remote sensing applications.</span></p>',
      'tags': ['unsupervised learning', 'sentinel-2'],
      'createdAt': '2023-05-11T19:15:20.586',
      'updatedAt': '2023-05-23T18:02:25.652',
      'likes': 1,
      'downloads': 4,
      'quality': 0},
     {'uid': 'auth0|616b0057af0c7500691a026e',
      'id': '645e3b2dc2f02fdd88c47b77',
      'name': 'AirbusAircraftDetection',
      'authors': ['-'],
      'source': '',
      'license': '-',
      'files': '6526977d7d4d50bd035d0342',
      'versions': [{'version_id': 1,
        'createdAt': '2023-10-11T14:37:38.155',
        'size': 91853048}],
      'description': '<p>Dataset extracted from <a href="https://www.kaggle.com/datasets/airbusgeo/airbus-aircrafts-sample-dataset" rel="noopener noreferrer" target="_blank">Kaggle</a>.</p><p><br></p><p><span style="color: rgb(60, 64, 67);">Aircrafts are usually seen on airports. Earth observation satellites like Airbus\' Pleiades twin satellites acquire pictures of airports all over the world on a regular basis. Deep Learning can be used to detect automatically the number, size and type of aircrafts present on the site. In turn, this can provide information about the activity of any airport.</span></p><p><br></p><p><span style="color: rgb(60, 64, 67);">License: </span>CC BY-NC-SA 4.0</p>',
      'tags': ['object detection', 'airbus'],
      'createdAt': '2023-05-11T19:15:20.586',
      'updatedAt': '2023-05-16T12:20:03.653',
      'likes': 1,
      'downloads': 5,
      'quality': 0},
     {'uid': 'auth0|616b0057af0c7500691a026e',
      'id': '645e3e4fc2f02fdd88c47b7a',
      'name': 'AirbusWindTurbinesPatches',
      'authors': ['-'],
      'source': '',
      'license': 'CC BY-NC-SA 4.0',
      'files': '6526977f7d4d50bd035d0343',
      'versions': [{'version_id': 1,
        'createdAt': '2023-10-11T14:37:38.155',
        'size': 1083685010}],
      'description': '<h3>Information extracted from <a href="https://www.kaggle.com/datasets/airbusgeo/airbus-wind-turbines-patches" rel="noopener noreferrer" target="_blank">Kaggle</a>.</h3><h3><br></h3><p><strong>Context</strong></p><p>Wind turbines make electricity from wind. Wind turns the propeller-like blades of a turbine around a rotor, which spins a generator, which creates electricity. Generating electricity from wind rather than from gas helps fight global warming. More and more states and private companies are investing in renewable energies and building huge wind turbines plants. Knowing where this wind turbines are located is essential and could help in energy production forecast. Deep Learning could help identify wind turbines on satellite image.</p><p><br></p><h3><strong>Content</strong></h3><p>This is very simple dataset which objective is to build a classifier of satellite images extract&nbsp;<strong>with</strong>&nbsp;or&nbsp;<strong>without</strong>&nbsp;wind turbines. Extracts of 128 x 128 pixels with wind turbines are located in a folder called&nbsp;<code style="background-color: rgb(241, 243, 244);">targets</code>&nbsp;; extracts without wind turbines are located in a folder called&nbsp;<code style="background-color: rgb(241, 243, 244);">background</code>. Images are extracted from satellite acquisitions from the Airbus&nbsp;<a href="https://www.intelligence-airbusds.com/en/8693-spot-67" rel="noopener noreferrer" target="_blank" style="color: rgb(32, 33, 36);">SPOT6 and SPOT7 satellites</a>&nbsp;which resolution is 1.5 meters per pixel. So extracts of 128 x 128 pixels represents roughly 192 meters on the ground which is compatible with the typical size of a wind turbine.</p><p><br></p><h3><strong>Acknowledgements</strong></h3><p>This dataset would not exists without the contribution of the Innovation team at Airbus DS GEO S.A. Thank you for all your hard work and the fun during the tagging and hacking sessions.</p><p><br></p><h3><strong>Inspiration</strong></h3><p>Building a classifier is a very common task in Deep Learning. When dealing with imagery, it is also very common to use&nbsp;<strong>convolutions</strong>&nbsp;to create CNN. By replacing the last fully connected layers of the model by 1-d convolutions, it is possible to create what is called a&nbsp;<strong>fully convolutional neural network</strong>&nbsp;a.k.a. FCN. This model can then be used on imagery of any size to build a detector. The technical paper is available here&nbsp;<a href="https://arxiv.org/abs/1411.4038" rel="noopener noreferrer" target="_blank" style="color: rgb(32, 33, 36);">https://arxiv.org/abs/1411.4038</a></p><p><br></p><p>License: CC BY-NC-SA 4.0</p>',
      'tags': ['image classification', 'airbus'],
      'createdAt': '2023-05-11T19:15:20.586',
      'updatedAt': '2023-05-31T13:50:51.915',
      'likes': 1,
      'downloads': 2,
      'quality': 0},
     {'uid': 'auth0|6461eed50d3e450fa7f48648',
      'id': '64633fdfc2f02fdd88c47b85',
      'name': 'RoadNet',
      'authors': ['Liu, Yahui; Yao, Jian; Lu, Xiaohu; Xia, Menghan; Wang, Xingbo; Liu, Yuan'],
      'source': 'https://github.com/yhlleo/RoadNet',
      'license': '-',
      'files': '652697817d4d50bd035d0344',
      'versions': [{'version_id': 1,
        'createdAt': '2023-10-11T14:37:38.155',
        'size': 948649414}],
      'description': '<p><a href="https://ieeexplore.ieee.org/document/8506600/figures#figures" rel="noopener noreferrer" target="_blank">Paper</a></p><p><br></p><p>A multi-task benchmark dataset used for extraction of road networks from VHR remotely sensed images in complex urban scenes.</p>',
      'tags': ['land cover', 'segmentation', 'object detection'],
      'createdAt': '2023-05-11T19:15:20.586',
      'updatedAt': '2023-05-24T14:25:29.963',
      'likes': 0,
      'downloads': 0,
      'quality': 0},
     {'uid': 'auth0|6461eed50d3e450fa7f48648',
      'id': '6463589e59028dfdbee33336',
      'name': 'SloveniaLandCover',
      'authors': ['Sinergise'],
      'source': 'http://eo-learn.sentinel-hub.com/',
      'license': '-',
      'files': '652697937d4d50bd035d0345',
      'versions': [{'version_id': 1,
        'createdAt': '2023-10-11T14:37:38.155',
        'size': 9957077222}],
      'description': '<p>Sample dataset of EOPatches, for the region of Slovenia, for the year 2019. This data can be used in remote sensing applications, such as land cover classification.</p><p><br></p><p><span style="color: rgb(0, 0, 0);">This example dataset will help you get started with Remote Sensing data and analysis in the open-source framework of eo-learn.</span></p><p><br></p>',
      'tags': ['sentinel-2', 'land cover', 'segmentation'],
      'createdAt': '2023-05-16T12:16:48.985',
      'updatedAt': '2023-05-24T14:21:20.939',
      'likes': 0,
      'downloads': 2,
      'quality': 0},
     {'uid': 'auth0|6461eed50d3e450fa7f48648',
      'id': '6463716b59028dfdbee33338',
      'name': 'ISPRS-Potsdam2D',
      'authors': ['Wuhan University; Lancaster University; University of Twente'],
      'source': 'https://opendatalab.com/ISPRS_Potsdam/download',
      'license': '-',
      'files': '652697aa7d4d50bd035d0346',
      'versions': [{'version_id': 1,
        'createdAt': '2023-10-11T14:37:38.155',
        'size': 13324219686}],
      'description': '<p><a href="https://arxiv.org/ftp/arxiv/papers/2109/2109.08937.pdf" rel="noopener noreferrer" target="_blank">Paper</a></p><p><br></p><p>The dataset contains 38 patches (of the same size), each consisting of a true orthophoto (TOP) extracted from a larger TOP mosaic and a DSM.</p><p><br></p><p>The ground sampling distance of both, the TOP and the DSM, is 5 cm. The DSM was generated via dense image matching with Trimble INPHO 5.6 software and Trimble INPHO OrthoVista was used to generate the TOP mosaic. In order to avoid areas without data (“holes”) in the TOP and the DSM, the patches were selected from the central part of the TOP mosaic and none at the boundaries. Remaining (very small) holes in the TOP and the DSM were interpolated.</p><p>The TOP come as TIFF files in different channel composistions, where each channel has a spectral resolution of 8bit.</p>',
      'tags': [],
      'createdAt': '2023-05-16T12:16:48.985',
      'updatedAt': '2023-05-24T14:19:03.823',
      'likes': 0,
      'downloads': 1,
      'quality': 0},
     {'uid': 'auth0|642adbfdb3da3ab51492d60a',
      'id': '646477ac59028dfdbee33341',
      'name': 'SEN12-FLOOD',
      'authors': ['Clément Rambour, Nicolas Audebert, Elise Koeniguer, Bertrand Le Saux, Michel Crucianu, Mihai Datcu, September 14, 2020, "SEN12-FLOOD : a SAR and Multispectral Dataset for Flood Detection ", IEEE Dataport, doi: https://dx.doi.org/10.21227/w6xz-s898.'],
      'source': 'https://mlhub.earth/data/sen12floods',
      'license': 'Creative Commons Attribution 4.0 International',
      'files': '652697bd7d4d50bd035d0347',
      'versions': [{'version_id': 1,
        'createdAt': '2023-10-11T14:37:38.155',
        'size': 10750956154}],
      'description': '<p>SEN12-FLOOD is a set of multimodal (SAR + multispectral) satellite image time-series for flood classification. See the paper <a href="https://radiantearth.blob.core.windows.net/mlhub/sen12floods/documentation.pdf" rel="noopener noreferrer" target="_blank">here</a>.</p><p><br></p><p>The observed areas correspond to 337 locations (cities and their surroundings ) in West and SouthEast Africa, Middle-East, and Australia where a flood event occurred during the considered period. The period of acquisition goes from December 2018 to May 2019. </p><p><br></p><p>For each location, the following data are provided: </p><ul><li> Time series of Sentinel-2 multispectral images. These images are composed of 12 bands, at 10m ground-sampling distance and are provided with Level 2A atmospheric correction. </li><li> Time series of Sentinel-1 Synthetic Aperture Radar (SAR) images. The images are provided with radiometric calibration and range doppler terrain correction based on the SRTM digital elevation model. For one acquisition, two raster images are available corresponding to the polarimetry channels VV and VH. </li><li> Time series of binary labels for each image / date: flood or no flood. The original dataset was split into 262 sequences for the train and 68 sequences for the test.</li></ul>',
      'tags': ['sentinel-1',
       'sentinel-2',
       'sar',
       'image classification',
       'flood detection'],
      'createdAt': '2023-05-16T12:16:48.985',
      'updatedAt': '2023-05-29T17:35:35.149',
      'likes': 0,
      'downloads': 14,
      'quality': 0},
     {'uid': 'auth0|6461eed50d3e450fa7f48648',
      'id': '6464899459028dfdbee33344',
      'name': 'Urban3dChallenge',
      'authors': ['Hirsh Goldberg; Myron Brown; Sean Wang'],
      'source': 'https://spacenet.ai/the-ussocom-urban-3d-competition/',
      'license': '-',
      'files': '652697d67d4d50bd035d0348',
      'versions': [{'version_id': 1,
        'createdAt': '2023-10-11T14:37:38.155',
        'size': 13913901752}],
      'description': '<p><a href="https://ieeexplore.ieee.org/document/8457973" rel="noopener noreferrer" target="_blank">Paper</a></p><p><br></p><p>This challenge published a large-scale dataset containing 2D orthrorectified RGB and 3D Digital Surface Models and Digital Terrain Models generated from commercial satellite imagery covering over 360 km of terrain and containing roughly 157,000 annotated building footprints. All imagery products are provided at 50 cm ground sample distance (GSD). This unique 2D/3D large scale dataset provides researchers an opportunity to utilize machine learning techniques to further improve state of the art performance.</p>',
      'tags': [],
      'createdAt': '2023-05-16T12:16:48.985',
      'updatedAt': '2023-05-24T14:11:36.119',
      'likes': 0,
      'downloads': 1,
      'quality': 0},
     {'uid': 'auth0|630cc8fe75e5e824b9e863c6',
      'id': '64649f3f59028dfdbee3334a',
      'name': 'tropical-cyclone-dataset',
      'authors': ['-'],
      'source': '',
      'license': '-',
      'files': '652697da7d4d50bd035d0349',
      'versions': [{'version_id': 1,
        'createdAt': '2023-10-11T14:37:38.155',
        'size': 2369002579}],
      'description': 'https://mlhub.earth/data/nasa_tropical_storm_competition',
      'tags': [],
      'createdAt': '2023-05-16T12:16:48.985',
      'updatedAt': '2023-05-16T12:16:48.985',
      'likes': 0,
      'downloads': 1,
      'quality': 0},
     {'uid': 'auth0|645df677f9c0b75b29963900',
      'id': '646640b359028dfdbee3335c',
      'name': 'Vessel-detection',
      'authors': ['RHEA Group'],
      'source': 'https://eodashboard.org/',
      'license': 'Dataset copyrighted under the ORCS project license. ',
      'files': '652697dc7d4d50bd035d034a',
      'versions': [{'version_id': 1,
        'createdAt': '2023-10-11T14:37:38.155',
        'size': 973498275}],
      'description': '<p>Detecting ships by automatically processing Sentinel-2 data (10 m spatial resolution) over well-defined Area Of Interest (AOI) to be used within ESA Euro Data Cube (EDC) infrastructure to support the Earth Observing Dashboard and RACE initiatives. The detection task is performed by means of a deep learning model using a customized Faster R-CNN architecture.</p><p><br></p><p>Learn more: <a href="https://eodashboard.org/story?id=shipping" rel="noopener noreferrer" target="_blank">https://eodashboard.org/story?id=shipping</a></p>',
      'tags': ['sentinel-2', 'image classification', 'object detection'],
      'createdAt': '2023-05-16T12:16:48.985',
      'updatedAt': '2023-06-27T15:21:24.039',
      'likes': 0,
      'downloads': 8,
      'quality': 0},
     {'uid': 'auth0|645df677f9c0b75b29963900',
      'id': '646642d659028dfdbee3335e',
      'name': 'Airplanes-detection',
      'authors': ['RHEA Group'],
      'source': 'https://eodashboard.org/',
      'license': 'Dataset copyrighted under the ORCS project license. ',
      'files': '652697dc7d4d50bd035d034b',
      'versions': [{'version_id': 1,
        'createdAt': '2023-10-11T14:37:38.155',
        'size': 41500516}],
      'description': '<p>Detecting parked airplanes by automatically processing Sentinel-2 data (10 m spatial resolution) over well-defined Area Of Interest (AOI) to be used within ESA Euro Data Cube (EDC) infrastructure to support the Earth Observing Dashboard and RACE initiatives. The detection task is performed by means of a deep learning model using a customized Faster R-CNN architecture.</p><p><br></p><p>Learn more: <a href="https://www.eodashboard.org/story?id=airports" rel="noopener noreferrer" target="_blank">https://www.eodashboard.org/story?id=airports</a></p>',
      'tags': ['object detection', 'sentinel-2', 'image classification'],
      'createdAt': '2023-05-16T12:16:48.985',
      'updatedAt': '2023-06-27T15:29:09.835',
      'likes': 0,
      'downloads': 2,
      'quality': 0},
     {'uid': 'auth0|6440fc22834ccb24b613fa5a',
      'id': '6467305859028dfdbee33362',
      'name': 'S2-SHIPS',
      'authors': ['Alina Ciocarlan (IMT Atlantique, 29280 Plouzané, France)'],
      'source': 'https://github.com/alina2204/contrastive_SSL_ship_detection',
      'license': 'MIT license',
      'files': '652697e77d4d50bd035d034c',
      'versions': [{'version_id': 1,
        'createdAt': '2023-10-11T14:37:38.155',
        'size': 6223750329}],
      'description': '<p>contains the COCO annotations files, the 12 spectral bands for each S2-SHIPS tile in a tif or numpy array version, the S2-SHIPS segmentation masks, the water masks and some pretrained backbones.</p>',
      'tags': ['object detection', 'sentinel-2'],
      'createdAt': '2023-05-16T12:16:48.985',
      'updatedAt': '2023-05-25T14:42:31.993',
      'likes': 0,
      'downloads': 9,
      'quality': 0},
     {'uid': 'auth0|64672e7ce74dbb9b67fd16e4',
      'id': '64674b4459028dfdbee33364',
      'name': 'SpaceNet-7',
      'authors': ['SpaceNet Partners'],
      'source': 'https://spacenet.ai/sn7-challenge/',
      'license': 'http://creativecommons.org/licenses/by-sa/4.0/',
      'files': '652697f67d4d50bd035d034d',
      'versions': [{'version_id': 1,
        'createdAt': '2023-10-11T14:37:38.155',
        'size': 9165250722}],
      'description': '<p><strong>SpaceNet 7</strong> Multi-Temporal Urban Development Challenge dataset (https://medium.com/the-downlinq/the-spacenet-7-multi-temporal-urban-development-challenge-dataset-release-9e6e5f65c8d5, https://spacenet.ai/sn7-challenge/)</p>',
      'tags': [],
      'createdAt': '2023-05-16T12:16:48.985',
      'updatedAt': '2023-05-23T17:36:41.007',
      'likes': 1,
      'downloads': 36,
      'quality': 0},
     {'uid': 'auth0|642adbfdb3da3ab51492d60a',
      'id': '646b3dcd59028dfdbee33372',
      'name': 'Sentinel-2-Cloud-Mask',
      'authors': ['Francis, Alistair, Mrziglod, John, Sidiropoulos, Panagiotis, & Muller, Jan-Peter. (2020). Sentinel-2 Cloud Mask Catalogue [Data set]. Zenodo. https://doi.org/10.5281/zenodo.4172871'],
      'source': 'https://zenodo.org/record/4172871#.ZHTGYexBz0p',
      'license': 'Creative Commons Attribution 4.0 International',
      'files': '652698117d4d50bd035d034e',
      'versions': [{'version_id': 1,
        'createdAt': '2023-10-11T14:37:38.155',
        'size': 15357118520}],
      'description': '<p>This dataset comprises cloud masks for 513 1022-by-1022 pixel subscenes, at 20m resolution, sampled random from the 2018 Level-1C Sentinel-2 archive.</p><p><br></p><p>You can see further information <a href="https://zenodo.org/record/4172871#.ZGs4QOxBz0o" rel="noopener noreferrer" target="_blank">here</a>.</p><p><br></p><p><br></p>',
      'tags': ['segmentation', 'sentinel-2'],
      'createdAt': '2023-05-16T12:16:48.985',
      'updatedAt': '2023-05-29T17:36:29.256',
      'likes': 0,
      'downloads': 0,
      'quality': 0},
     {'uid': 'auth0|642adbfdb3da3ab51492d60a',
      'id': '646b448d59028dfdbee33374',
      'name': 'PASTIS',
      'authors': ['Sainte Fare Garnot Vivien, & Landrieu Loic. (2021). PASTIS - Panoptic Segmentation of Satellite image TIme Series (1.0) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.5012942'],
      'source': 'https://zenodo.org/record/5012942#.ZHTFgOxBz0o',
      'license': 'Creative Commons Attribution 4.0 International',
      'files': '652698457d4d50bd035d034f',
      'versions': [{'version_id': 1,
        'createdAt': '2023-10-11T14:37:38.155',
        'size': 28760245504}],
      'description': '<p>PASTIS (Panoptic Segmentation of Satellite Image Time Series with Convolutional Temporal Attention Networks) is a benchmark dataset for panoptic and semantic segmentation of agricultural parcels from satellite time series. It contains 2,433 patches within the French metropolitan territory with panoptic annotations (instance index + semantic label for each pixel). Each patch is a Sentinel-2 multispectral image time series of variable length. </p><p><br></p><p>This dataset is the original PASTIS dataset for semantic and panoptic segmentation on Sentinel-2 time series.</p><p><br></p><p>You can see further information <a href="https://arxiv.org/abs/2107.07933" rel="noopener noreferrer" target="_blank">here</a>.</p>',
      'tags': ['segmentation',
       'sentinel-2',
       'agriculture',
       'land cover',
       'image classification'],
      'createdAt': '2023-05-16T12:16:48.985',
      'updatedAt': '2023-05-29T17:32:37.596',
      'likes': 0,
      'downloads': 7,
      'quality': 0},
     {'uid': 'auth0|64675bc4a7419507f5c69052',
      'id': '646b814559028dfdbee33378',
      'name': 'FlodNet',
      'authors': ['-'],
      'source': '',
      'license': '-',
      'files': '652698717d4d50bd035d0350',
      'versions': [{'version_id': 1,
        'createdAt': '2023-10-11T14:37:38.155',
        'size': 25001433318}],
      'description': '<p>FloodNet: A High Resolution Aerial Imagery Dataset for Post Flood Scene Understanding</p><p><br></p><p>Visual scene understanding is the core task in making any crucial decision in any computer vision system. Although popular computer vision datasets like Cityscapes, MS-COCO, PASCAL provide good benchmarks for several tasks (e.g. image classification, segmentation, object detection), these datasets are hardly suitable for post disaster damage assessments. On the other hand, existing natural disaster datasets include mainly satellite imagery which have low spatial resolution and a high revisit period. Therefore, they do not have a scope to provide quick and efficient damage assessment tasks. Unmanned Aerial Vehicle(UAV) can effortlessly access difficult places during any disaster and collect high resolution imagery that is required for aforementioned tasks of computer vision. To address these issues we present a high resolution UAV imagery, FloodNet, captured after the hurricane Harvey. This dataset demonstrates the post flooded damages of the affected areas. The images are labeled pixel-wise for semantic segmentation task and questions are produced for the task of visual question answering. FloodNet poses several challenges including detection of flooded roads and buildings and distinguishing between natural water and flooded water. With the advancement of deep learning algorithms, we can analyze the impact of any disaster which can make a precise understanding of the affected areas. In this paper, we compare and contrast the performances of baseline methods for image classification, semantic segmentation, and visual question answering on our dataset.</p><p><br></p><p>paper: https://arxiv.org/abs/2012.02951</p><p>dataset: https://github.com/BinaLab/FloodNet-Challenge-EARTHVISION2021</p>',
      'tags': [],
      'createdAt': '2023-05-16T12:16:48.985',
      'updatedAt': '2023-05-22T21:17:54.778',
      'likes': 0,
      'downloads': 1,
      'quality': 0},
     {'uid': 'auth0|616b0057af0c7500691a026e',
      'id': '646cf14046f51deed53f6d5b',
      'name': 'EuroCrops',
      'authors': ['Schneider, Maja; Chan, Ayshah; Körner, Marco'],
      'source': 'https://zenodo.org/record/7851838',
      'license': 'CC BY 4.0',
      'files': '6526987f7d4d50bd035d0351',
      'versions': [{'version_id': 1,
        'createdAt': '2023-10-11T14:37:38.155',
        'size': 8489703546}],
      'description': '<p>Version 7 (Apr 21, 2023)</p><p><br></p><p><strong style="color: rgb(51, 51, 51);">EuroCrops</strong><span style="color: rgb(51, 51, 51);">&nbsp;is a dataset collection combining all publicly available self-declared crop reporting datasets from countries of the European Union.</span></p><p><br></p><p><span style="color: rgb(51, 51, 51);">Learn more: </span><a href="https://github.com/maja601/EuroCrops#vectordata" rel="noopener noreferrer" target="_blank">https://github.com/maja601/EuroCrops#vectordata</a></p>',
      'tags': ['segmentation', 'agriculture', 'vector'],
      'createdAt': '2023-05-23T15:57:29.413',
      'updatedAt': '2023-05-24T11:01:13.8',
      'likes': 1,
      'downloads': 0,
      'quality': 0},
     {'uid': 'auth0|6462a7c70d3e450fa7f4acde',
      'id': '646f55c8f11dc70cb67317df',
      'name': 'open-cities-test',
      'authors': ['Global Facility for Disaster Reduction and Recovery (GFDRR)'],
      'source': 'https://mlhub.earth/data/open_cities_ai_challenge',
      'license': 'CC-BY-4.0',
      'files': '6526988f7d4d50bd035d0352',
      'versions': [{'version_id': 1,
        'createdAt': '2023-10-11T14:37:38.155',
        'size': 9003672752}],
      'description': '<p><span style="color: rgb(26, 32, 39);">Open Cities AI Challenge Test Dataset</span></p><p><br></p><p><span style="color: rgb(26, 32, 39);">This dataset was developed as part of a challenge to segment building footprints from aerial imagery. The goal of the challenge was to accelerate the development of more accurate, relevant, and usable open-source AI models to support mapping for disaster risk management in African cities. The data consists of drone imagery from 10 different cities and regions across Africa.</span></p>',
      'tags': [],
      'createdAt': '2023-05-23T19:54:36.294',
      'updatedAt': '2023-06-01T13:19:42.382',
      'likes': 0,
      'downloads': 1,
      'quality': 0},
     {'uid': 'auth0|642adbfdb3da3ab51492d60a',
      'id': '6474acf3f11dc70cb67317e9',
      'name': 'PASTIS-R',
      'authors': ['Vivien SAINTE FARE GARNOT, & Loic LANDRIEU. (2021). PASTIS-R - Panoptic Segmentation of Radar and Optical Satellite image TIme Series [Data set]. Zenodo. https://doi.org/10.5281/zenodo.5735646'],
      'source': 'https://zenodo.org/record/5735646#.ZHTE7uxBz0o',
      'license': 'Creative Commons Attribution 4.0 International',
      'files': '652698f27d4d50bd035d0353',
      'versions': [{'version_id': 1,
        'createdAt': '2023-10-11T14:37:38.155',
        'size': 53695489854}],
      'description': '<p>PASTIS (Panoptic Segmentation of Satellite Image Time Series with Convolutional Temporal Attention Networks) is a benchmark dataset for panoptic and semantic segmentation of agricultural parcels from satellite time series. It contains 2,433 patches within the French metropolitan territory with panoptic annotations (instance index + semantic label for each pixel). Each patch is a Sentinel-2 multispectral image time series of variable lentgh.</p><p><br></p><p>This dataset is the extended PASTIS dataset with aligned radar Sentinel-1 observations for all 2433 patches in addition to the Sentinel-2 images. For each patch, there have been added approximately 70 observations of Sentinel-1 in ascending orbit, and 70 observations in descending orbit. PASTIS-R can be used to evaluate optical-radar fusion methods for parcel-based classification, semantic segmentation, and panoptic segmentation.</p><p><br></p><p>You can see further information <a href="https://arxiv.org/abs/2112.07558v1" rel="noopener noreferrer" target="_blank">here</a>.</p>',
      'tags': ['sar',
       'image classification',
       'segmentation',
       'sentinel-1',
       'agriculture',
       'land cover',
       'sentinel-2'],
      'createdAt': '2023-05-23T19:54:36.294',
      'updatedAt': '2023-05-29T17:33:09.591',
      'likes': 0,
      'downloads': 0,
      'quality': 0},
     {'uid': 'auth0|6462a7c70d3e450fa7f4acde',
      'id': '64776d6898edc5f751083891',
      'name': 'open-cities-tt1-source',
      'authors': ['Global Facility for Disaster Reduction and Recovery (GFDRR)'],
      'source': 'https://mlhub.earth/data/open_cities_ai_challenge',
      'license': 'CC-BY-4.0',
      'files': '6526992b7d4d50bd035d0354',
      'versions': [{'version_id': 1,
        'createdAt': '2023-10-11T14:37:38.155',
        'size': 32363731670}],
      'description': '<p><span style="color: rgb(26, 32, 39);">Open Cities AI Challenge Train Tier 1 Source Imagery</span></p><p><br></p><p><span style="color: rgb(26, 32, 39);">This dataset was developed as part of a challenge to segment building footprints from aerial imagery. The goal of the challenge was to accelerate the development of more accurate, relevant, and usable open-source AI models to support mapping for disaster risk management in African cities. The data consists of drone imagery from 10 different cities and regions across Africa.</span></p>',
      'tags': [],
      'createdAt': '2023-05-31T17:06:35.422',
      'updatedAt': '2023-06-01T13:19:28.047',
      'likes': 0,
      'downloads': 0,
      'quality': 0},
     {'uid': 'auth0|6462a7c70d3e450fa7f4acde',
      'id': '647860b298edc5f751083893',
      'name': 'open-cities-tt2-source',
      'authors': ['Global Facility for Disaster Reduction and Recovery (GFDRR)'],
      'source': 'https://mlhub.earth/data/open_cities_ai_challenge',
      'license': 'CC-BY-4.0',
      'files': '652699757d4d50bd035d0355',
      'versions': [{'version_id': 1,
        'createdAt': '2023-10-11T14:37:38.155',
        'size': 41143613634}],
      'description': '<p><span style="color: rgb(26, 32, 39);">Open Cities AI Challenge Train Tier 2 Source Imagery</span></p><p><br></p><p><span style="color: rgb(26, 32, 39);"><span class="ql-cursor">\ufeff</span>This dataset was developed as part of a challenge to segment building footprints from aerial imagery. The goal of the challenge was to accelerate the development of more accurate, relevant, and usable open-source AI models to support mapping for disaster risk management in African cities. The data consists of drone imagery from 10 different cities and regions across Africa.</span></p>',
      'tags': [],
      'createdAt': '2023-06-01T11:45:16.731',
      'updatedAt': '2023-06-01T13:22:04.136',
      'likes': 0,
      'downloads': 0,
      'quality': 0},
     {'uid': 'auth0|64454081a1131bb5f16ec4e0',
      'id': '6487589b24d9f398bfb7bb18',
      'name': 'LandcoverAI',
      'authors': ['-'],
      'source': '',
      'license': '-',
      'files': '652699787d4d50bd035d0356',
      'versions': [{'version_id': 1,
        'createdAt': '2023-10-11T14:37:38.155',
        'size': 1538212277}],
      'description': '',
      'tags': [],
      'createdAt': '2023-06-09T10:41:01.958',
      'updatedAt': '2023-06-09T10:41:01.958',
      'likes': 0,
      'downloads': 3,
      'quality': 0},
     {'uid': 'auth0|616b0057af0c7500691a026e',
      'id': '64888a8e471c3b884b24c022',
      'name': 'xview2',
      'authors': ['-'],
      'source': '',
      'license': '-',
      'files': '65269a237d4d50bd035d0358',
      'versions': [{'version_id': 1,
        'createdAt': '2023-10-11T14:37:38.155',
        'size': 54882773479}],
      'description': '',
      'tags': [],
      'createdAt': '2023-06-13T16:45:39.852',
      'updatedAt': '2023-06-13T16:45:39.852',
      'likes': 1,
      'downloads': 0,
      'quality': 0},
     {'uid': 'auth0|616b0057af0c7500691a026e',
      'id': '64896b59f0d696bce297b36f',
      'name': 'BigEarthNet',
      'authors': ['Remote Sensing Image Analysis (RSiM) Group',
       ' the Database Systems and Information Management (DIMA) Group at the Technische Universität Berlin (TU Berlin)'],
      'source': 'https://bigearth.net/',
      'license': 'Community Data License Agreement - Permissive - Version 1.0 ',
      'files': '65269ba97d4d50bd035d035b',
      'versions': [{'version_id': 1,
        'createdAt': '2023-10-11T14:37:38.155',
        'size': 129301889692}],
      'description': '<p><em style="color: rgb(33, 37, 41);">BigEarthNet</em><span style="color: rgb(33, 37, 41);">&nbsp;is a benchmark archive, consisting of&nbsp;</span><strong style="color: rgb(50, 107, 52);">590,326</strong><span style="color: rgb(33, 37, 41);">&nbsp;pairs of&nbsp;</span><strong style="color: rgb(50, 107, 52);">Sentinel-1</strong><span style="color: rgb(33, 37, 41);">&nbsp;and&nbsp;</span><strong style="color: rgb(50, 107, 52);">Sentinel-2</strong><span style="color: rgb(33, 37, 41);">&nbsp;image patches. The first version (v1.0-beta) of&nbsp;</span><em style="color: rgb(33, 37, 41);">BigEarthNet</em><span style="color: rgb(33, 37, 41);">&nbsp;includes only Sentinel 2 images. Recently, it has been enriched by Sentinel-1 images to create a multi-modal&nbsp;</span><em style="color: rgb(33, 37, 41);">BigEarthNet</em><span style="color: rgb(33, 37, 41);">&nbsp;benchmark archive (called also as BigEarthNet-MM).</span></p>',
      'tags': ['image classification', 'sentinel-2', 'sentinel-1'],
      'createdAt': '2023-06-14T09:18:17.368',
      'updatedAt': '2023-07-20T12:10:09.209',
      'likes': 1,
      'downloads': 4,
      'quality': 0},
     {'uid': 'auth0|642adbfdb3da3ab51492d60a',
      'id': '64bfbb6f2a65dcd4ae2ca613',
      'name': 'EuroSAT-RGB-STAC',
      'authors': ['Patrick Helber'],
      'source': 'http://madm.dfki.de/downloads',
      'license': 'MIT License',
      'files': '65269baa7d4d50bd035d035c',
      'versions': [{'version_id': 1,
        'createdAt': '2023-10-11T14:37:38.155',
        'size': 458654511}],
      'description': '<p><strong>EuroSAT: A land use and land cover classification dataset based on Sentinel-2 satellite images.</strong></p><p><br></p><p>This is the RGB version of<strong>&nbsp;</strong><a href="https://www.eotdl.com/datasets/EuroSAT" rel="noopener noreferrer" target="_blank">EuroSAT</a> with STAC metadata.</p><p><br></p><p><a href="https://arxiv.org/abs/1709.00029" rel="noopener noreferrer" target="_blank">Paper</a></p><p><a href="http://madm.dfki.de/downloads" rel="noopener noreferrer" target="_blank">Alternative download link</a></p><p><br></p><p><span style="color: rgb(0, 0, 0);">Land use and land cover classification using Sentinel-2 satellite images.</span></p><p><br></p><p><span style="color: rgb(0, 0, 0);">The Sentinel-2 satellite images are openly and freely accessible provided in the Earth observation program Copernicus. We present a novel dataset based on Sentinel-2 satellite images covering 13 spectral bands and consisting out of 10 classes with in total 27,000 labeled and geo-referenced images.</span></p><p><br></p>',
      'tags': ['image classification', 'land cover', 'land use', 'sentinel-2'],
      'createdAt': '2023-07-19T13:19:12.136',
      'updatedAt': '2023-07-26T16:13:56.092',
      'likes': 0,
      'downloads': 8,
      'quality': 0},
     {'uid': 'auth0|642adbfdb3da3ab51492d60a',
      'id': '64c788902a65dcd4ae2ca629',
      'name': 'EuroSAT-STAC',
      'authors': ['Patrick Helber'],
      'source': 'http://madm.dfki.de/downloads',
      'license': 'MIT License',
      'files': '65269bb07d4d50bd035d035e',
      'versions': [{'version_id': 1,
        'createdAt': '2023-10-11T14:37:38.155',
        'size': 4249698396}],
      'description': '<p><strong>EuroSAT: A land use and land cover classification dataset based on Sentinel-2 satellite images.</strong></p><p><br></p><p><a href="https://arxiv.org/abs/1709.00029" rel="noopener noreferrer" target="_blank">Paper</a></p><p><br></p><p><span style="color: rgb(0, 0, 0);">Land use and land cover classification using Sentinel-2 satellite images with STAC.</span></p><p><br></p><p><span style="color: rgb(0, 0, 0);">The Sentinel-2 satellite images are openly and freely accessible provided in the Earth observation program Copernicus. We present a novel dataset based on Sentinel-2 satellite images covering 13 spectral bands and consisting out of 10 classes with in total 27,000 labeled and geo-referenced images.</span></p>',
      'tags': ['land cover', 'sentinel-2', 'image classification', 'land use'],
      'createdAt': '2023-07-19T13:19:12.136',
      'updatedAt': '2023-09-13T17:23:52.97',
      'likes': 0,
      'downloads': 8,
      'quality': 0},
     {'uid': 'auth0|642adbfdb3da3ab51492d60a',
      'id': '65006c9a751700cadfbd28fb',
      'name': 'COWC',
      'authors': ['Nathan Mundhenk',
       ' Goran Konjevod',
       ' Wesam A. Sakla',
       ' Kofi Boakye'],
      'source': 'https://gdo152.llnl.gov/cowc/',
      'license': 'GNU AFFERO GENERAL PUBLIC LICENSE',
      'files': '65269c817d4d50bd035d0361',
      'versions': [{'version_id': 1,
        'createdAt': '2023-10-11T14:37:38.155',
        'size': 39935370223}],
      'description': '<p><span style="color: rgb(0, 0, 0);">The&nbsp;</span><strong style="color: rgb(0, 0, 0);">Cars Overhead With Context (COWC)&nbsp;</strong><span style="color: rgb(0, 0, 0);">data set is a large set of annotated cars from overhead. It is useful for training a device such as a deep neural network to learn to detect and/or count cars. More information can be obtained by&nbsp;</span><strong style="color: rgb(0, 0, 0);">reading the paper</strong><span style="color: rgb(0, 0, 0);">&nbsp;</span><a href="http://gdo-datasci.ucllnl.org/cowc/mundhenk_et_al_eccv_2016.pdf" rel="noopener noreferrer" target="_blank">here</a><span style="color: rgb(0, 0, 0);">. </span></p><p><br></p><p><span style="color: rgb(0, 0, 0);">The dataset has the following attributes:</span></p><ul><li class="ql-align-justify"><span style="background-color: transparent;">Data from overhead at 15 cm per pixel resolution at ground (all data is EO).&nbsp;</span></li><li class="ql-align-justify"><span style="background-color: transparent;">Data from six distinct locations:&nbsp;</span><a href="http://www2.isprs.org/commissions/comm3/wg4/tests.html" rel="noopener noreferrer" target="_blank" style="background-color: transparent;">Toronto</a><span style="background-color: transparent;">&nbsp;Canada,&nbsp;</span><a href="http://www.linz.govt.nz/" rel="noopener noreferrer" target="_blank" style="background-color: transparent;">Selwyn</a>&nbsp;<span style="background-color: transparent;">New Zealand,&nbsp;</span><a href="http://www2.isprs.org/commissions/comm3/wg4/tests.html" rel="noopener noreferrer" target="_blank" style="background-color: transparent;">Potsdam</a><span style="background-color: transparent;">&nbsp;and&nbsp;</span><a href="http://www2.isprs.org/commissions/comm3/wg4/tests.html" rel="noopener noreferrer" target="_blank" style="background-color: transparent;">Vaihingen</a>&nbsp;<span style="background-color: transparent;">&nbsp;Germany,&nbsp;</span><a href="https://www.sdms.afrl.af.mil/index.php?collection=csuav" rel="noopener noreferrer" target="_blank" style="background-color: transparent;">Columbus</a>&nbsp;Ohio<span style="background-color: transparent;">&nbsp;and&nbsp;</span><a href="http://gis.utah.gov/data/aerial-photography/" rel="noopener noreferrer" target="_blank" style="background-color: transparent;">Utah</a>&nbsp;<span style="background-color: transparent;">United States.&nbsp;</span></li><li class="ql-align-justify"><span style="background-color: transparent;">32,716 unique annotated cars. 58,247 unique negative examples.</span></li><li class="ql-align-justify"><span style="background-color: transparent;">Intentional selection of hard negative examples.</span></li><li class="ql-align-justify"><span style="background-color: transparent;">Established baseline for detection and counting tasks.</span></li><li class="ql-align-justify"><span style="background-color: transparent;">Extra testing scenes for use after validation.</span></li></ul><p><br></p><p><br></p>',
      'tags': ['object detection', 'sentinel-2'],
      'createdAt': '2023-09-08T11:29:26.627',
      'updatedAt': '2023-09-13T16:38:24.989',
      'likes': 0,
      'downloads': 0,
      'quality': 0},
     {'uid': 'auth0|642adbfdb3da3ab51492d60a',
      'id': '6501e112751700cadfbd2904',
      'name': 'Stanford-Drone-dataset',
      'authors': ['A. Robicquet', ' A. Sadeghian', ' A. Alahi', ' S. Savarese'],
      'source': 'https://cvgl.stanford.edu/projects/uav_data/',
      'license': 'Creative Commons Attribution-NonCommercial-ShareAlike 3.0 License',
      'files': '65269da77d4d50bd035d0364',
      'versions': [{'version_id': 1,
        'createdAt': '2023-10-11T14:37:38.155',
        'size': 71002113639}],
      'description': '<p><span style="color: rgb(0, 0, 0);">When humans navigate a crowed space such as a university campus or the sidewalks of a busy street, they follow common sense rules based on social etiquette. In order to enable the design of new algorithms that can fully take advantage of these rules to better solve tasks such as target tracking or trajectory forecasting, it is needed to have access to better data. </span></p><p><br></p><p><span style="color: rgb(0, 0, 0);">To that end, this dataset is a large scale dataset that collects images and videos of various types of agents (not just pedestrians, but also bicyclists, skateboarders, cars, buses, and golf carts) that navigate in a real world outdoor environment such as a university campus. In the above images, pedestrians are labeled in pink, bicyclists in red, skateboarders in orange, and cars in green</span></p>',
      'tags': ['object detection'],
      'createdAt': '2023-09-08T11:29:26.627',
      'updatedAt': '2023-09-13T20:37:09.812',
      'likes': 0,
      'downloads': 0,
      'quality': 0},
     {'uid': 'auth0|616b0057af0c7500691a026e',
      'id': '6503f8a3d05a1b62cc273ea4',
      'name': 'eurosat-rgb',
      'description': '',
      'tags': [],
      'createdAt': '2023-09-15T06:10:21.544',
      'updatedAt': '2023-09-15T08:42:30.275',
      'likes': 0,
      'downloads': 4,
      'quality': 1,
      'size': 0,
      'catalog': {'type': 'Catalog',
       'id': 'eurosat-rgb',
       'stac_version': '1.0.0',
       'description': 'EuroSAT-RGB dataset',
       'links': [{'rel': 'self',
         'href': '/home/juan/Desktop/eotdl/tutorials/data/EuroSAT-STAC/catalog.json',
         'type': 'application/json'},
        {'rel': 'root', 'href': './catalog.json', 'type': 'application/json'},
        {'rel': 'child',
         'href': './source/collection.json',
         'type': 'application/json'},
        {'rel': 'child',
         'href': './labels/collection.json',
         'type': 'application/json'}],
       'extent': None,
       'license': None,
       'stac_extensions': None,
       'summaries': None,
       'properties': None,
       'assets': None,
       'bbox': None,
       'collection': None},
      'versions': [{'version_id': 1,
        'createdAt': '2023-10-11T14:37:38.155',
        'size': 1773680}]},
     {'uid': 'auth0|616b0057af0c7500691a026e',
      'id': '6503f994d05a1b62cc273fdd',
      'name': 'eurosat-rgb-q2',
      'description': '',
      'tags': [],
      'createdAt': '2023-09-15T06:10:21.544',
      'updatedAt': '2023-09-15T08:29:04.656',
      'likes': 0,
      'downloads': 3,
      'quality': 2,
      'size': 0,
      'catalog': {'type': 'Catalog',
       'id': 'eurosat-rgb-q2',
       'stac_version': '1.0.0',
       'description': 'EuroSAT-RGB dataset',
       'links': [{'rel': 'self',
         'href': '/home/juan/Desktop/eotdl/tutorials/data/EuroSAT-Q2/catalog.json',
         'type': 'application/json'},
        {'rel': 'root', 'href': './catalog.json', 'type': 'application/json'},
        {'rel': 'child',
         'href': './source/collection.json',
         'type': 'application/json'},
        {'rel': 'child',
         'href': './labels/collection.json',
         'type': 'application/json'}],
       'stac_extensions': ['https://raw.githubusercontent.com/earthpulse/ml-dataset/main/json-schema/schema.json'],
       'ml-dataset:name': 'EuroSAT Q2 Dataset',
       'ml-dataset:tasks': ['image classification'],
       'ml-dataset:inputs-type': ['satellite imagery'],
       'ml-dataset:annotations-type': 'raster',
       'ml-dataset:version': '0.1.0',
       'ml-dataset:splits': ['Training', 'Validation', 'Test'],
       'ml-dataset:quality-metrics': [{'name': 'spatial-duplicates',
         'values': [{'item': 'Industrial_1273', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1117', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1121', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1641', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_259', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_435', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_674', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_905', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_238', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_631', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_2292', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1952', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1980', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_524', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_689', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1967', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_305', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1184', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_2193', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1015', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1532', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_146', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_962', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1543', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1328', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1721', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_2024', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1233', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_94', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_910', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_364', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1096', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_512', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1291', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_59', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_124', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1899', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_78', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_448', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1920', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1434', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_421', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_125', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_2216', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_265', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_354', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1327', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1104', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1923', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1312', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_2486', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_239', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_212', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1978', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1378', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1535', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_2037', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1881', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1797', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1739', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1225', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_665', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1710', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1708', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_253', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1754', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_2359', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_40', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1491', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_2281', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_2471', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_767', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_496', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1049', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_807', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1376', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_2479', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_850', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1124', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1955', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_594', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1469', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1073', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_299', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_2367', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_153', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1959', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1522', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1694', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_419', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_882', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_1215', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_2062', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_233', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_2063', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_2394', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_412', 'duplicate': 'Industrial_1743'},
          {'item': 'Industrial_702', 'duplicate': 'Industrial_1743'}],
         'total': 98},
        {'name': 'classes-balance',
         'values': [{'class': 'Industrial', 'total': 99, 'percentage': 10},
          {'class': 'Forest', 'total': 99, 'percentage': 10},
          {'class': 'HerbaceousVegetation', 'total': 99, 'percentage': 10},
          {'class': 'PermanentCrop', 'total': 99, 'percentage': 10},
          {'class': 'Highway', 'total': 99, 'percentage': 10},
          {'class': 'Residential', 'total': 99, 'percentage': 10},
          {'class': 'SeaLake', 'total': 99, 'percentage': 10},
          {'class': 'River', 'total': 99, 'percentage': 10},
          {'class': 'AnnualCrop', 'total': 99, 'percentage': 10},
          {'class': 'Pasture', 'total': 99, 'percentage': 10}]}],
       'extent': None,
       'license': None,
       'ml-dataset:split-items': None,
       'summaries': None,
       'properties': None,
       'assets': None,
       'bbox': None,
       'collection': None},
      'versions': [{'version_id': 1,
        'createdAt': '2023-10-11T14:37:38.155',
        'size': 453353}]},
     {'uid': 'auth0|616b0057af0c7500691a026e',
      'id': '6526accffd974011abc2413a',
      'name': 'EuroSAT-small',
      'authors': ['juan'],
      'source': 'http://km.com',
      'license': 'open',
      'files': '6526accffd974011abc2413b',
      'versions': [{'version_id': 1,
        'createdAt': '2023-10-11T16:08:47.864',
        'size': 643464},
       {'version_id': 2, 'createdAt': '2023-10-11T16:08:47.864', 'size': 643464},
       {'version_id': 3, 'createdAt': '2023-10-12T07:14:16.642', 'size': 643464},
       {'version_id': 4, 'createdAt': '2023-10-12T07:14:16.642', 'size': 643464},
       {'version_id': 5, 'createdAt': '2023-10-12T07:14:16.642', 'size': 643464},
       {'version_id': 6, 'createdAt': '2023-10-12T07:14:16.642', 'size': 643464},
       {'version_id': 7, 'createdAt': '2023-10-12T07:14:16.642', 'size': 0},
       {'version_id': 8, 'createdAt': '2023-10-12T07:14:16.642', 'size': 0},
       {'version_id': 9, 'createdAt': '2023-11-02T13:11:36.142', 'size': 643562},
       {'version_id': 10, 'createdAt': '2023-11-02T13:13:39.237', 'size': 643562}],
      'description': '',
      'tags': [],
      'createdAt': '2023-10-11T16:08:47.865',
      'updatedAt': '2023-11-02T15:09:08.656',
      'likes': 0,
      'downloads': 0,
      'quality': 0},
     {'uid': 'auth0|645df677f9c0b75b29963900',
      'id': '653a31c09171acf769e2731b',
      'name': 'test-q0',
      'authors': [''],
      'source': 'https://www.eotdl.com',
      'license': '',
      'files': '653a31c09171acf769e2731c',
      'versions': [{'version_id': 1,
        'createdAt': '2023-10-12T07:14:16.642',
        'size': 518196}],
      'description': '',
      'tags': [],
      'createdAt': '2023-10-25T16:08:29.666',
      'updatedAt': '2023-10-26T11:31:21.189',
      'likes': 0,
      'downloads': 0,
      'quality': 0},
     {'uid': 'auth0|616b0057af0c7500691a026e',
      'id': '6543ba3f68ea46a6677efec9',
      'name': 'Boadella-BiDS23',
      'authors': ['Fran Martin', 'Juan B. Pedro'],
      'source': 'https://github.com/earthpulse/eotdl/blob/develop/tutorials/workshops/bids23/04_creating.ipynb',
      'license': 'free',
      'files': '6543ba3f68ea46a6677efeca',
      'versions': [{'version_id': 1,
        'createdAt': '2023-11-02T13:11:36.142',
        'size': 17812745},
       {'version_id': 2,
        'createdAt': '2023-11-02T13:11:36.142',
        'size': 17825361}],
      'description': '',
      'tags': [],
      'createdAt': '2023-11-02T13:11:36.142',
      'updatedAt': '2023-11-02T16:05:28.953',
      'likes': 0,
      'downloads': 0,
      'quality': 0}]



As you can see, here you get all the information about the dataset, not only the name (author, license, versions, etc). This is why the API is ideal for building third party applications on top of EOTDL.


```python
datasets = requests.get("https://api.eotdl.com/datasets?match=eurosat-small&limit=1").json()
[(d['name'], d['id'], d['files'], len(d['versions'])) for d in datasets]	
```




    [('EuroSAT-small', '6526accffd974011abc2413a', '6526accffd974011abc2413b', 9)]



In fact, the library (and CLI) are built on top of the API, so you can achieve the same functionality (or even better!) on your own applications.


```python
files = requests.get("https://api.eotdl.com/datasets/6526accffd974011abc2413a/files?version=2").json()
len(files)
```




    6




```python
files[0]
```




    {'filename': 'Forest/Forest_3.tif',
     'version': 1,
     'checksum': '3e7bb982f9db5f7dabc556016c3d081dfb1fb73d'}



Some API calls requires you to be authenticated. You can do that with as follows:

- Use the `auth/login` endpoint to get a login URL and a code
- Navigate to the login URL to login
- Use the `auth/token` endpoint to get a token with the provided code
- Use the token to authenticate your requests


```python
import os

token = '...'

file = files[0]
filename = file["filename"]
filepath = f'data/{filename}'

os.makedirs(os.path.dirname(filepath), exist_ok=True)
response = requests.get(
    f'https://api.eotdl.com/datasets/6526accffd974011abc2413a/download/{filename}?version=1', 
    headers={'Authorization': f'Bearer {token}'},
    stream=True
)
response.raise_for_status()

with open(filepath, 'wb') as file:
    for chunk in response.iter_content(chunk_size=8192):
        file.write(chunk)

```


    ---------------------------------------------------------------------------

    HTTPError                                 Traceback (most recent call last)

    /home/juan/Desktop/eotdl/tutorials/workshops/bids23/01_exploring_datasets_and_models..ipynb Cell 53 line 1
          <a href='vscode-notebook-cell://ssh-remote%2Bharley/home/juan/Desktop/eotdl/tutorials/workshops/bids23/01_exploring_datasets_and_models..ipynb#Y144sdnNjb2RlLXJlbW90ZQ%3D%3D?line=8'>9</a> os.makedirs(os.path.dirname(filepath), exist_ok=True)
         <a href='vscode-notebook-cell://ssh-remote%2Bharley/home/juan/Desktop/eotdl/tutorials/workshops/bids23/01_exploring_datasets_and_models..ipynb#Y144sdnNjb2RlLXJlbW90ZQ%3D%3D?line=9'>10</a> response = requests.get(
         <a href='vscode-notebook-cell://ssh-remote%2Bharley/home/juan/Desktop/eotdl/tutorials/workshops/bids23/01_exploring_datasets_and_models..ipynb#Y144sdnNjb2RlLXJlbW90ZQ%3D%3D?line=10'>11</a>     f'https://api.eotdl.com/datasets/6526accffd974011abc2413a/download/{filename}?version=1', 
         <a href='vscode-notebook-cell://ssh-remote%2Bharley/home/juan/Desktop/eotdl/tutorials/workshops/bids23/01_exploring_datasets_and_models..ipynb#Y144sdnNjb2RlLXJlbW90ZQ%3D%3D?line=11'>12</a>     headers={'Authorization': f'Bearer {token}'},
         <a href='vscode-notebook-cell://ssh-remote%2Bharley/home/juan/Desktop/eotdl/tutorials/workshops/bids23/01_exploring_datasets_and_models..ipynb#Y144sdnNjb2RlLXJlbW90ZQ%3D%3D?line=12'>13</a>     stream=True
         <a href='vscode-notebook-cell://ssh-remote%2Bharley/home/juan/Desktop/eotdl/tutorials/workshops/bids23/01_exploring_datasets_and_models..ipynb#Y144sdnNjb2RlLXJlbW90ZQ%3D%3D?line=13'>14</a> )
    ---> <a href='vscode-notebook-cell://ssh-remote%2Bharley/home/juan/Desktop/eotdl/tutorials/workshops/bids23/01_exploring_datasets_and_models..ipynb#Y144sdnNjb2RlLXJlbW90ZQ%3D%3D?line=14'>15</a> response.raise_for_status()
         <a href='vscode-notebook-cell://ssh-remote%2Bharley/home/juan/Desktop/eotdl/tutorials/workshops/bids23/01_exploring_datasets_and_models..ipynb#Y144sdnNjb2RlLXJlbW90ZQ%3D%3D?line=16'>17</a> with open(filepath, 'wb') as file:
         <a href='vscode-notebook-cell://ssh-remote%2Bharley/home/juan/Desktop/eotdl/tutorials/workshops/bids23/01_exploring_datasets_and_models..ipynb#Y144sdnNjb2RlLXJlbW90ZQ%3D%3D?line=17'>18</a>     for chunk in response.iter_content(chunk_size=8192):


    File ~/miniconda3/envs/eotdl/lib/python3.8/site-packages/requests/models.py:1021, in Response.raise_for_status(self)
       1016     http_error_msg = (
       1017         f"{self.status_code} Server Error: {reason} for url: {self.url}"
       1018     )
       1020 if http_error_msg:
    -> 1021     raise HTTPError(http_error_msg, response=self)


    HTTPError: 401 Client Error: Unauthorized for url: https://api.eotdl.com/datasets/6526accffd974011abc2413a/download/Forest/Forest_3.tif?version=1

