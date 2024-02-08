<p align="center">
  <a href="https://www.eotdl.com/">
    <img src="https://raw.githubusercontent.com/earthpulse/eotdl/main/eotdl/eotdl.png" alt="EOTDL" style="width: 75%;"/>
  </a>
</p>

<p align="center">Explore, download, create and share your own Training Datasets and Machine Learning models for Earth Observation</p>
<p align="center"><a href="https://www.eotdl.com/">Website</a> · <a href="https://www.eotdl.com/docs">Documentation</a> · <a href="https://www.eotdl.com/datasets">Datasets</a> · <a href="https://www.eotdl.com/blog">Blog</a></p>

<p align="center">
    <a href="https://pypi.python.org/pypi/eotdl">
        <img src="https://img.shields.io/pypi/v/eotdl.svg" alt="NPM Version" />
    </a>
</p>

This is the main library and CLI for the **Earth Observation Training Data Lab** (EOTDL), a complete environment that allows you, among other things, to:

- Explore and download Training Datasets (TDS) for Earth Observation (EO) applications.
- Create and upload your own TDS by combining and annotating EO data from different sources.
- Train Machine Learning (ML) models using the hosted TDS in the cloud with multi-GPU machines.
- Explore and download pre-trianed ML models for EO applications.

In our blog you will find tutorials to learn how leverage the EOTDL to create and use TDS and ML models for your own EO applications.

## Why EOTDL?

One of the most limiting factors of AI for EO applications is the scarcity of suitable and accessible Training Datasets (TDS). As the name suggests, TDS are used to train an AI model to perform a specific task. Currently, the main barrier is that gathering and labelling EO data is a convoluted process. Some techniques exist that can help alleviate this issue, for example transfer learning or unsupervised learning, but annotated data is always required for fine-tuning and final validation of AI models.

Generating TDS is time consuming and expensive. Data access is usually limited and costly, especially for Very High Resolution (VHR) images that allow objects like trees to be clearly identified. In some cases, domain experts or even in-person (in-situ) trips are required to manually confirm the objects in a satellite image are correctly annotated with a high degree of quality. This results in the field of AI for EO applications lagging when compared to other fields, impeding the development of new applications and limiting the full potential of AI in EO.

The European Space Agency (ESA) Earth Observation Training Data Lab (EOTDL) will address key limitations and capability gaps for working with Machine Learning (ML) training data in EO by providing a set of open-source tools to create, share, and improve datasets as well as training ML algorithms in the cloud. EOTDL will also offer an online repository where datasets and models can be explored and accessed.