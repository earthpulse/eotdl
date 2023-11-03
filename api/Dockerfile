FROM python:3.8

RUN pip install --upgrade pip 
RUN pip install fastapi
RUN pip install uvicorn
RUN pip install pytest  
RUN pip install pytest-watch  
RUN pip install pytest-cov
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


COPY ./api /api
