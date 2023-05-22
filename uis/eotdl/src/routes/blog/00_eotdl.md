---
title: Welocome to EOTDL
date: '2023-04-26T00:00:00.000Z'
description: This post will give you an overview of the EOTDL and how to get started.
tags: getting started
---

# Welcome to EOTDL 🥳

Welcome to the **Earth Observation Training Data Lab** (EOTDL), a complete environment that allows you, among other things, to:

- Explore and download Training Datasets (TDS) for Earth Observation (EO) applications.
- Create and upload your own TDS by combining and annotating EO data from different sources.
- Train Machine Learning (ML) models using the hosted TDS in the cloud with multi-GPU machines.
- Explore and download pre-trianed ML models for EO applications.

In our blog you will find tutorials to learn how leverage the EOTDL to create and use TDS and ML models for your own EO applications.

## Why EOTDL ?

One of the most limiting factors of AI for EO applications is the scarcity of suitable and accessible Training Datasets (TDS). As the name suggests, TDS are used to train an AI model to perform a specific task. Currently, the main barrier is that gathering and labelling EO data is a convoluted process. Some techniques exist that can help alleviate this issue, for example transfer learning or unsupervised learning, but annotated data is always required for fine-tuning and final validation of AI models.

Generating TDS is time consuming and expensive. Data access is usually limited and costly, especially for Very High Resolution (VHR) images that allow objects like trees to be clearly identified. In some cases, domain experts or even in-person (in-situ) trips are required to manually confirm the objects in a satellite image are correctly annotated with a high degree of quality. This results in the field of AI for EO applications lagging when compared to other fields, impeding the development of new applications and limiting the full potential of AI in EO.

The European Space Agency (ESA) Earth Observation Training Data Lab (EOTDL) will address key limitations and capability gaps for working with Machine Learning (ML) training data in EO by providing a set of open-source tools to create, share, and improve datasets as well as training ML algorithms in the cloud. EOTDL will also offer an online repository where datasets and models can be explored and accessed.

## Getting involved

### Github repository

EOTDL is an open-source project. You can find the code in our [Github](https://github.com/earthpulse/eotdl) repository. There you will be able to track the progress and instructions for [Contributing](https://github.com/earthpulse/eotdl/blob/main/CONTRIBUTING.md).

### Discord server

To get in touch with the team and other users, join our [Discord](https://discord.gg/hYxc5AJB92) server. There you will be able to ask questions, share your feedback and get involved in the platform evolution.

## Getting started

In this section you will learn the basics of EOTDL and how to install the different components. To know more, check the [documentation](/docs).

### The EOTDL ecosystem

The EOTDL is composed by a set of libraries, user interfaces, command line tools, and APIs. 

You can install the CLI using pip.

```
pip install eotdl-cli
````

To verify the installation you can run the help command, which will give you a list of all the available commands in the CLI.

```
eotdl-cli --help
```

You can install the library using pip.

```
pip install eotdl
```

You don’t have to install anything to interact with user interfaces or the API.

Our API offers an interactive [documentation](https://api.eotdl.com/docs) that can be used to explore the different endpoints and test them.

### Authenticate

Some of the operations within EOTDL require authentication. Learn how to authenticate in the [documentation](/docs/getting-started/authenticate).



### Training Datasets

The main feature that EOTDL offers is a repository of Training Datasets (TDS). Users can explore available datasets and download them for training ML models, for example.

### Quality Levels

The datasets hosted on the EOTDL are categorized into for quality levels:

- **Q0**: raw datasets in the form of a compressed archive without any metadata. This level is ideal for easy and fast upload/download of small datasets.
- **Q1**: datasets with STAC metadata and cloud-optimized data and no QA. These datasets can leverage a limited set of EOTDL features.
- **Q2**: datasets with STAC metadata with the EOTDL custom extensions and automated QA. These datasets can leverage the full potential of the EOTDL.
- **Q3**: Q2 datasets that are manually curated. These datasets are the most reliable and can be used as benchmark datasets for training machine learning models.

EOTDL offers functionality to easily create datasets and perform automated quality checks on Q1+ datasets, which metrics are reported in the STAC metadata.

> Currently, only Q0 datasets are supported. We will update this post and the documentation as new features are available.

## Next steps

Check our next post to start working with Q0 datasets.
