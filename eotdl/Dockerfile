FROM python:3.8

RUN pip install --upgrade pip 
RUN pip install poetry 

WORKDIR /eotdl

COPY . /eotdl

RUN poetry install --no-interaction 