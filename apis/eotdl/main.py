from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .routers import auth, datasets, tags, admin  # , migrate

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(datasets.router)
app.include_router(tags.router)
app.include_router(admin.router)
# app.include_router(migrate.router)

logging.basicConfig(
    filename="/tmp/eotdl-api.log",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

VERSION = "2023.09.14"


@app.get("/", name="home", include_in_schema=False)
async def root():
    return {
        "name": "eotdl",
        "version": VERSION,
        "description": "Earth Observation Training Data Lab",
        "contact": "support@eotdl.com",
    }
