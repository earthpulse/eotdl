# Use Case A - Unsupervised Learning

In this use case we show how te leverage EOTDL functionality to create a large dataset for unsupervised pre-training of convolutional neural networks.

## Dataset

The code to generate the dataset can be found in [`dataset.ipynb`](dataset.ipynb).

Our starting point is the [`Satellogic` dataset](https://satellogic-earthview.s3.us-west-2.amazonaws.com/index.html) a collection of over 7M 1m resolution Satellogic public images, captured between July 1, 2022, and December 30, 2022.

From this dataset, we leverage EOTDL functionality to find matching `Sentinel 1` and `Sentinel 2` images for the same bounding box and close in time. The code can be found in [`find_matches.py`](find_matches.py) for a simplified script and [`find_matches_chunks.py`](find_matches_chunks.py) for an optimized version to find matches for all the original dataset.

The original dataset and a 1M sample with matches has been ingested into EOTDL at https://www.eotdl.com/datasets/SatellogicDataset. Only metadata is ingested.

Once the matches are found, we can filter and download the desired matches for the desired task. The code can be found in [`download_images.py`](download_images.py). The script allows to set a cloud cover threshold for Sentinel 2 filtering and width and height of the resulting matches.

For this use case, we downloaded approximately 250k pairs of Sentinel 2 and Satellogic images. However, the code can be easily modified to download more matches, including Sentinel 1. 

## Training

After filtering and downloading the images, we can train unsupervised models for fine-tuning on downstream tasks. The overall workflow is descirbed in the [`training.ipynb`](training.ipynb) notebook, while the actual training code is available in [`train.py`](train.py).

We use the [`Barlow Twins`](https://arxiv.org/abs/2103.03230) method to pre-train [`ResNet`](https://arxiv.org/abs/1512.03385) models, which works fine with reduced computational resources.

For pre-training foundation models with larger computational resources, the use of Transformers+MAE is recommended. In that case, the process to generate the pre-training dataset can be easily adapted from this use case.