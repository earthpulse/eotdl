---
name: MultitaskLearning
authors: 
  - Juan B. Pedro
license: free
source: https://github.com/earthpulse/eotdl/tree/main/tutorials/usecases/useCaseC/pipeline
thumbnail: https://ruder.io/content/images/2017/05/weighting_using_uncertainty.png
---

# Multitask Learning

This pipeline includes:

1 - Training a classification, segmentation and multi-tasking models with a small dataset of 100 images labeled with SCANEO.
2 - An inference API to use the models in SCANEO for assisted labelling that you can start with `uv run uvicorn inference:app --port 8001`.
3 - A notebook to test the inference API.

This pipeline shows how to enable Active Learning with SCANEO and EOTDL.

The code is available at https://github.com/earthpulse/eotdl/tree/main/tutorials/usecases/useCaseC/pipeline.