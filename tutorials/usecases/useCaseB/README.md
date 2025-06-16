# Use Case B - Superresolution

In this use case we show how to leverage EOTDL functionality to create a dataset and ML model for superresolution.

## Dataset

Our starting point is the [`Satellogic` dataset](https://www.eotdl.com/datasets/SatellogicDataset) generated in [Use Case A](../useCaseA/README.md). This dataset contains over 7M Satellogic images, with a 1M sample of Sentinel 2 and Sentinel 1 matches. For this use case, we will only use the Sentinel 2 matches to train a model for superresolution, from 10m Sentinel 2 to 5m (2x superresolution) using the 1m Satellogic images as targets.

The code to stage the dataset from EOTDL and download the raw imagery can be found in [`dataset.ipynb`](dataset.ipynb) and [`download_images.py`](download_images.py) respectively.

## Training

After filtering and downloading the images, we can train a model for superresolution. Once the model is trained, we can export it to ONNX format and ingest it into EOTDL. The overall workflow is descirbed in the [`training.ipynb`](training.ipynb) notebook, while the actual training code is available in [`train.py`](train.py). 