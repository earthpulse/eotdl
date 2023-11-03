from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
import logging
import os

from .auth import key_auth
from ..src.repos.mongo.client import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/logs/{tail}", include_in_schema=False)
def logs(isAdmin: bool = Depends(key_auth), tail: int = 10):
    try:
        # return last lines of log file
        with open("/tmp/eotdl-api.log", "r") as f:
            lines = f.readlines()
            return lines[-tail:]
    except Exception as e:
        logger.exception("logs")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/env", include_in_schema=False)
def env_vars(isAdmin: bool = Depends(key_auth)):
    try:
        return os.environ
    except Exception as e:
        logger.exception("logs")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/init-db", include_in_schema=False)
def initialize_db(isAdmin: bool = Depends(key_auth)):
    try:
        db = get_db()
        collections = db.list_collection_names()
        for collection in collections:
            db[collection].drop()
        db["tiers"].insert_many(
            [
                {
                    "name": "free",
                    "limits": {
                        "datasets": {"upload": 3, "download": 3, "count": 10},
                        "models": {"upload": 3, "download": 3, "count": 10},
                    },
                },
                {
                    "name": "dev",
                    "limits": {
                        "datasets": {"upload": 100, "download": 100, "count": 100},
                        "models": {"upload": 100, "download": 100, "count": 100},
                    },
                },
            ]
        )
        db["tags"].insert_many(
            [
                {"name": "agriculture"},
                {"name": "sentinel-2"},
                {"name": "sentinel-1"},
                {"name": "object-detection"},
                {"name": "segmentation"},
            ]
        )
        return "done"
    except Exception as e:
        logger.exception("logs")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
