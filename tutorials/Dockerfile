FROM continuumio/miniconda3

RUN pip install notebook
RUN pip install python-dotenv
RUN pip install pystac
RUN pip install rasterio
RUN pip install stac_validator
RUN pip install geomet
RUN pip install PyJWT
RUN pip install pydantic

RUN mkdir /ipynbs
WORKDIR /ipynbs