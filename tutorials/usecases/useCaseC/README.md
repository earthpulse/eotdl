# Use Case C - Multi-task Learning

In this use case we show how te leverage EOTDL and SCANEO functionality to create a dataset and ML models for multi-task learning on high resolution satellite imagery.

## Dataset

Our starting point is the [`Satellogic` dataset](https://satellogic-earthview.s3.us-west-2.amazonaws.com/index.html) a collection of over 7M 1m resolution Satellogic public images, captured between July 1, 2022, and December 30, 2022.

As part of [`use case A`](../useCaseA/README.md) we already prepared and ingested the dataset into EOTDL at https://www.eotdl.com/datasets/SatellogicDataset.

From there, we first sample 100 random images from the dataset and label them using [`SCANEO`](https://github.com/earthpulse/scaneo).

## Training

After filtering and downloading the images, we can train the models and ingest them into EOTDL. The overall workflow is descirbed in the [`training.ipynb`](training.ipynb) notebook.

An inference API can be started with [`inference.py`](inference.py) to use SCANEO assisted labeling capabilities. You can start it with `uv run uvicorn inference:app --port 8001`.