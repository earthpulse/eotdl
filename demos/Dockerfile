FROM python:3.8

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libc-dev \
    make \
    python3-lxml \
    gdal-bin \
    libgdal-dev \
    git \
    ca-certificates \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip 
RUN pip install pydantic
RUN pip install pymongo  
RUN pip install pyjwt
RUN pip install requests
RUN pip install jupyter