# Road extraction on Sentinel 2

This use case demonstrates how to create a road extraction dataset on Sentinel 2 data.

## Data

The datasets is based on the [Massachusets Roads Datasets](https://www.eotdl.com/datasets/MassachusettsRoadsDataset), which contains 1171 aerial images of the state of Massachusetts with associated road labels. From the aerial images, we download Sentinel 2 images for the same bounding boxes and match the road labels to the Sentinel 2 images. The code is available in the [`dataset.ipynb`](dataset.ipynb) notebook.

## Training

The overall training workflow is available in the [`training.ipynb`](training.ipynb) notebook, and the standalone training script is available in the [`training.py`](training.py) file.