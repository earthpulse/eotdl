FROM python:3.12

ENV PROMETHEUS_MULTIPROC_DIR /var/tmp/prometheus_multiproc_dir
RUN mkdir $PROMETHEUS_MULTIPROC_DIR \
    && chown www-data $PROMETHEUS_MULTIPROC_DIR \
    && chmod g+w $PROMETHEUS_MULTIPROC_DIR

ENV PATH /opt/conda/bin:$PATH

RUN apt-get update --fix-missing && \
    apt-get install -y wget libarchive-dev && \   
    wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    /opt/conda/bin/conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main && \
    /opt/conda/bin/conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r && \
    /opt/conda/bin/conda install -c conda-forge mamba -y && \
    /opt/conda/bin/conda clean -afy && \
    apt-get purge -y --auto-remove wget && \
    apt-get clean

RUN mamba install -c conda-forge xcube_geodb>=1.0.9

RUN pip install --upgrade pip && \
    pip install \
        fastapi \
        uvicorn \
        pytest \
        pytest-asyncio \
        pytest-watch \
        pytest-cov \
        pytest-mock \
        pydantic \
        pymongo \
        minio \
        pyjwt \
        requests \
        auth0-python \
        python-multipart \
        httpx \
        boto3 \
        pystac \
        stac_validator \
        geopandas \
        pyarrow \
        starlette_exporter \
        geomet \
        rasterio \
        duckdb \
        "pandas>=2.3.0" \
        stac_geoparquet

COPY ./api /api
