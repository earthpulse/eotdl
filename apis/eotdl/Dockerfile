FROM python:3.8
# FROM continuumio/miniconda3

# Set the environment variables for Conda
ENV PATH /opt/conda/bin:$PATH

# Install Miniconda, mamba and the missing library
RUN apt-get update --fix-missing && \
    apt-get install -y wget libarchive-dev && \   
    wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    /opt/conda/bin/conda install -c conda-forge mamba -y && \
    /opt/conda/bin/conda clean -afy && \
    apt-get purge -y --auto-remove wget && \
    apt-get clean

# Install xcube_geodb using mamba (conda takes forever)
RUN mamba install -c conda-forge xcube_geodb

RUN pip install --upgrade pip 
RUN pip install fastapi
RUN pip install uvicorn
RUN pip install pytest  
RUN pip install pytest-asyncio
RUN pip install pytest-watch  
RUN pip install pytest-cov
RUN pip install pytest-mock
RUN pip install pydantic
RUN pip install pymongo  
RUN pip install minio  
RUN pip install pyjwt
RUN pip install requests
RUN pip install auth0-python
RUN pip install python-multipart 
RUN pip install httpx
RUN pip install boto3
RUN pip install pystac
RUN pip install stac_validator
RUN pip install geopandas