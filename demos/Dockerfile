FROM continuumio/miniconda3

RUN conda install -c conda-forge xcube_geodb
RUN pip install notebook
RUN pip install python-dotenv

RUN mkdir /ipynbs
WORKDIR /ipynbs