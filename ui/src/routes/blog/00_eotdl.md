---
title: Welcome to EOTDL
date: '2023-11-04T00:00:00.000Z'
description: This post will give you an overview of the EOTDL and how to get started.
tags: getting started
link: https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/00_eotdl.ipynb
---

# The Earth Observation Training Data Lab

## Background

One of the most limiting factors of AI for EO applications is the scarcity of suitable and accessible **Training Datasets** (TDS). As the name suggests, TDS are used to train an AI model to perform a specific task. Currently, the main barrier is that gathering and labelling EO data is a convoluted process. Some techniques exist that can help alleviate this issue, for example transfer learning or unsupervised learning, but annotated data is always required for fine-tuning and final validation of AI models.
 
Generating TDS is time consuming and expensive. Data access is usually limited and costly, especially for Very High Resolution (VHR) images that allow objects like trees to be clearly identified. In some cases, domain experts or even in-person (in-situ) trips are required to manually confirm the objects in a satellite image are correctly annotated with a high degree of quality. This results in the field of AI for EO applications lagging when compared to other fields, impeding the development of new applications and limiting the full potential of AI in EO.

## EOTDL

The Earth Observation Training Data Lab (EOTDL) address these limitations and gaps for working with Machine Learning (ML) training data in EO by providing, one one hand, a set of open-source tools to create, share, and improve datasets as well as training ML algorithms in the cloud. On the other hand, EOTDL will is also an online repository where datasets and models can be explored and downloaded.

EOTDL is a project funded by [ESA](https://www.esa.int/), and developed by [Earthpulse](https://earthpulse.ai/) (project lead), [EOX](https://eox.at/), [Brockmann Consult](https://www.brockmann-consult.de/), [Sinergise](https://www.sinergise.com/) and [SpaceTec Partners](https://www.spacetec.partners/).

## Ecosystem

- EOTDL is built on top of OS software, and it is also OS [https://github.com/earthpulse/eotdl](https://github.com/earthpulse/eotdl)
- Users can access (Sentinel) data for dataset creation, selecting datas source, time range and areas of interest.
- Metadata for data curation and quality assurance is generated following the STAC specification. Automatic QA mechanisms and versioning is applied during the process of dataset ingestion.
- Engineering tools enable reproducible feature engineering, labelling, bias discoverability, etc. Training ML models in the cloud with multi-GPU machines is transparently enabled.
- The EOTDL is accessible at multiple levels: user interfaces, web APIs, CLI and Python library (+ wrappers).


## Who is this for?

The EOTDL is available to **everyone** and free to use.

You may find it interesting if:

- You are a data scientist or ML engineer working with EO data: you can use the EOTDL to create and share datasets, and train models in the cloud.
- You are a domain expert (e.g. forestry, agriculture, etc.) and want to explore the potential of AI for your field: you can explore, try and download the hosted models.
- You are a developer and want to contribute to the project: you can contribute to the open-source codebase, documentation, datasets and models.
- You are a student or researcher and want to learn about AI for EO: you can use the EOTDL to download datasets and train your models.
- And many more!

## Community

EOTDL is open source and community driven. We welcome contributions from everyone!

- Github: [https://github.com/earthpulse/eotdl](https://github.com/earthpulse/eotdl)
- Discord: [https://discord.gg/hYxc5AJB92](https://discord.gg/hYxc5AJB92)

We encourage you to join the Discord server now if you haven't already. We will be there to answer any questions you may have during the tutorial session, as well as after the event. You will also get updates on the project and be able to interact with other users, as well as provide feedback and suggestions and get involved in the evolution of the platform for the coming years.

## Let's start!

Check the notebooks in this folder to get started with the EOTDL. Feel free to ask any questions in the Discord server!
