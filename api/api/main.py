from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

import prometheus_client.multiprocess
from prometheus_client import CollectorRegistry, make_asgi_app

from .routers.auth import (
    login,
    logout,
    me,
    token,
    update_user_data,
    credentials,
    accept_terms_and_conditions,
    api_keys,
)
from .routers.tags import retrieve_tags
from .routers.datasets import (
    create_dataset,
    retrieve_dataset,
    ingest_dataset,
    # download_dataset,
    # update_dataset,
    # upload_large_dataset_files,
    # delete_dataset,
)
# from .routers.models import (
#     retrieve_models,
#     create_model,
#     ingest_model,
#     download_model,
#     upload_large_model_files,
#     update_model,
#     delete_model,
# )
# from .routers import admin, migrate

VERSION = "2025.01.30"

tags_metadata = [
    {
        "name": "auth",
        "description": "Operations with authentication. Login, logout, user information and token generation.",
    },
    {
        "name": "tags",
        "description": "Operations with tags. Retrieve tags.",
    },
    {
        "name": "datasets",
        "description": "Operations with datasets. Explore, ingest, retrieve or download datasets.",
    },
    {
        "name": "models",
        "description": "Operations with models. Explore, ingest, retrieve or download models.",
    },
]

description = """
The EOTDL API allows you, among other things, to:

* Explore and stage Training Datasets (TDS) for Earth Observation (EO) applications.
* Create and upload your own TDS by combining and annotating EO data from different sources.
* Train Machine Learning (ML) models using the hosted TDS in the cloud with multi-GPU machines.
* Explore and stage pre-trianed ML models for EO applications.
"""

app = FastAPI(
    title="EOTDL API",
    description=description,
    summary="Earth Observation Training Data Lab (EOTDL) API.",
    version=VERSION,
    terms_of_service="https://www.eotdl.com/TermsConditions.pdf",
    contact={
        "name": "EOTDL support",
        "url": "https://www.eotdl.com/",
        "mail": "support@eotdl.com",
    },
    openapi_tags=tags_metadata,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# auth
app.include_router(login.router, prefix="/auth", tags=["auth"])
app.include_router(logout.router, prefix="/auth", tags=["auth"])
app.include_router(me.router, prefix="/auth", tags=["auth"])
app.include_router(token.router, prefix="/auth", tags=["auth"])
app.include_router(update_user_data.router, prefix="/auth", tags=["auth"])
app.include_router(credentials.router, prefix="/auth", tags=["auth"])
app.include_router(accept_terms_and_conditions.router, prefix="/auth", tags=["auth"])
app.include_router(api_keys.router, prefix="/auth", tags=["auth"])
# tags
app.include_router(retrieve_tags.router, prefix="/tags", tags=["tags"])
# dataset
app.include_router(create_dataset.router, prefix="/datasets", tags=["datasets"])
app.include_router(retrieve_dataset.router, prefix="/datasets", tags=["datasets"])
app.include_router(ingest_dataset.router, prefix="/datasets", tags=["datasets"])
# app.include_router(download_dataset.router, prefix="/datasets", tags=["datasets"])
# app.include_router(update_dataset.router, prefix="/datasets", tags=["datasets"])
# app.include_router(
#     upload_large_dataset_files.router, prefix="/datasets", tags=["datasets"]
# )
# app.include_router(delete_dataset.router, prefix="/datasets", tags=["datasets"])
# # files
# # app.include_router(delete_dataset.router, prefix="/datasets", tags=["datasets"])
# # models
# app.include_router(retrieve_models.router, prefix="/models", tags=["models"])
# app.include_router(create_model.router, prefix="/models", tags=["models"])
# app.include_router(ingest_model.router, prefix="/models", tags=["models"])
# app.include_router(download_model.router, prefix="/models", tags=["models"])
# app.include_router(upload_large_model_files.router, prefix="/models", tags=["models"])
# app.include_router(update_model.router, prefix="/models", tags=["models"])
# app.include_router(delete_model.router, prefix="/models", tags=["models"])
# other
# app.include_router(admin.router)
# app.include_router(migrate.router)


def make_metrics_app():
    # Use multiprocess collector
    # https://github.com/prometheus/client_python#multiprocess-mode-eg-gunicorn
    registry = CollectorRegistry()
    prometheus_client.multiprocess.MultiProcessCollector(registry)
    return make_asgi_app(registry=registry)


metrics_app = make_metrics_app()
app.mount("/metrics", metrics_app)


logging.basicConfig(
    filename="/tmp/eotdl-api.log",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


@app.get("/", name="home", include_in_schema=False)
async def root():
    return {
        "name": "eotdl",
        "version": VERSION,
        "description": "Earth Observation Training Data Lab",
        "contact": "support@eotdl.com",
    }
