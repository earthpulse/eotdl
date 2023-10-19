# Earth Observation Training Data Lab

[![image](https://img.shields.io/pypi/v/eotdl.svg)](https://pypi.python.org/pypi/eotdl)

## Workshops

- BiDS 2023 ([notebook](workshops/bids23/README.md))

## Tutorials

### Datasets

1. Introducing the EOTDL ([notebook](notebooks/00_eotdl.ipynb))
2. Creating and ingesting Q0 datasets ([notebook](notebooks/01_q0_datasets.ipynb))
3. Creating and ingesting Q1 datasets ([notebook](notebooks/02_q1_datasets.ipynb))
4. Creating and ingesting Q2 datasets ([notebook](notebooks/03_q2_datasets.ipynb))

### Sentinel Hub

1. Authenticate in Sentinel Hub ([notebook](notebooks/10_sh_authenticate.ipynb))
2. Search imagery from Sentinel Hub ([notebook](notebooks/11_sh_search.ipynb))
3. Download imagery from Sentinel Hub ([notebook](notebooks/12_sh_download.ipynb))
4. Format the download data directory from Sentinel Hub ([notebook](notebooks/13_sh_format.ipynb))
5. Introducing the Sentinel Hub parameters ([notebook](notebooks/14_sh_parameters.ipynb))

### STAC

1. Generate STAC metadata ([notebook](notebooks/20_stac.ipynb))
2. Generate STAC metadata with extensions ([notebook](notebooks/21_stac_extensions.ipynb))
3. Introducing the STACDataFrame labeling strategy ([notebook](notebooks/22_stac_df_labeling.ipynb))
2. Introducing the STACDataFrame items parser ([notebook](notebooks/23_stac_item_parsers.ipynb))
3. Generate STAC labels generated from SCANEO ([notebook](notebooks/24_stac_labels_scaneo.ipynb))
4. Generate STAC labels from the filename ([notebook](notebooks/25_stac_labels_name.ipynb))
5. Add the ML-Dataset STAC extension to a Catalog ([notebook](notebooks/26_stac_ml_dataset.ipynb))
6. Calculate Quality metrics from your Catalog with the ML-Dataset extension ([notebook](notebooks/27_ml_dataset_quality_metrics.ipynb))
6. Get a GeoDataFrame from STAC items ([notebook](notebooks/28_stac_to_geodataframe.ipynb))
7. Export STAC to GeoDB and back from it ([notebook](notebooks/29_stac_to_geodb.ipynb))

### Do it yourself

1. Introducing the Do it yourself in EOTDL ([notebook](notebooks/30_do_it_yourself.ipynb))
2. Create your own STAC item parser ([notebook](notebooks/31_create_your_own_parser.ipynb))
3. Create your own STACDataFrame labeler ([notebook](notebooks/32_create_your_own_df_labeler.ipynb))
4. Create your own STAC labeler ([notebook](notebooks/33_create_your_own_stac_labeler.ipynb))
5. Add a new STAC extension to the EOTDL ([notebook](notebooks/34_add_stac_extension.ipynb))