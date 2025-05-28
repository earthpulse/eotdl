---
title: PANGAEA Benchmark now available in EOTDL
date: '2025-05-07T01:00:00.000Z'
description: We present the PANGAEA Benchmark, a new set of datasets for benchmarking the performance of Earth Observation Foundation Models.
tags: benchmark, datasets, models, pangaea
link: https://github.com/earthpulse/eotdl/blob/main/ui/src/routes/blog/pangaea.md
---

# PANGAEA Benchmark now available in EOTDL

While geospatial foundation models (GFMs) have proliferated rapidly, their evaluations remain inconsistent and narrow. Existing works often utilize suboptimal downstream datasets (e.g., EuroSAT) and tasks (e.g., land cover classification), which constrain comparability and real-world usability. Additionally, a lack of diversity in evaluation protocols, including image resolution and sensor types, further complicates the extensive assessments of GFM performance.

To bridge this gap, PANGAEA emerges as a standardized evaluation protocol that incorporates a wide-ranging selection of datasets, tasks, resolutions, and sensor types, establishing a robust and widely applicable benchmark for GFMs.

![pangaea](/blog/pangaea/geofmbenchmark.png)

## Datasets

The PANGAEA Benchmark includes the following datasets:

- [PASTIS-HD](https://www.eotdl.com/datasets/PASTIS-HD)
- [xView2](https://www.eotdl.com/datasets/xView2)
- [crop-type-mapping-south-sudan](https://www.eotdl.com/datasets/crop-type-mapping-south-sudan)
- [Five-Billion-Pixels](https://www.eotdl.com/datasets/Five-Billion-Pixels)
- [DynamicEarthNet](https://www.eotdl.com/datasets/DynamicEarthNet)
- [sen1floods11](https://www.eotdl.com/datasets/sen1floods11)
- [SpaceNet7](https://www.eotdl.com/datasets/SpaceNet7)
- [ai4smallfarms](https://www.eotdl.com/datasets/ai4smallfarms)
- [HLS-Burn-Scars](https://www.eotdl.com/datasets/HLS-Burn-Scars)
- [MADOS-Marine-Debris-Oil-Spill](https://www.eotdl.com/datasets/MADOS-Marine-Debris-Oil-Spill)

You can stage any of these datasets using the EOTDL CLI, for example:

```bash
eotdl datasets get PASTIS-HD --path .
```

Explore all the [datasets](/datasets) in EOTDL selecting the `PANGAEA` tag.

Learn more about the PANGAEA Benchmark in the [official repository](https://github.com/VMarsocci/pangaea-bench).

## Models

Alongisde the benchmark datasets, we also provide a set of models already benchmarked.

- [SSL4EO-S12](https://www.eotdl.com/models/SSL4EO-S12)
- [SpectralGPT](http://eotdl.com/models/SpectralGPT)
- [Scale-MAE](https://www.eotdl.com/models/Scale-MAE)
- [RemoteCLIP](http://eotdl.com/models/RemoteCLIP)
- [Prithvi](https://www.eotdl.com/models/Prithvi)
- [GFM-Swin](https://www.eotdl.com/models/GFM-Swin)
- [DOFA](https://www.eotdl.com/models/DOFA)
- [CROMA](https://www.eotdl.com/models/CROMA)