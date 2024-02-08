from fastapi.exceptions import HTTPException
from fastapi import Depends, APIRouter
from fastapi.security import HTTPBearer, APIKeyHeader
import logging
import os

from ...src.usecases.user import persist_user, retrieve_user_by_key
from ...src.usecases.auth import parse_token

logger = logging.getLogger(__name__)

token_auth_scheme = HTTPBearer(auto_error=False)
api_key_auth_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)


def admin_key_auth(api_key: str = Depends(api_key_auth_scheme)):
    if not api_key or api_key != os.environ.get("ADMIN_API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return


def key_auth(api_key: str = Depends(api_key_auth_scheme)):
    if not api_key:
        return None
    try:
        return retrieve_user_by_key(api_key).model_dump()
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid API key")


def token_auth(token: str = Depends(token_auth_scheme)):
    if not token:
        return None
    try:
        return parse_token(token.credentials)
    except Exception as e:
        logger.exception("get_current_user")
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user(api_key_user=Depends(key_auth), token: str = Depends(token_auth)):
    if not (api_key_user or token):
        raise HTTPException(status_code=401, detail="Not authenticated")
    data = api_key_user or token
    return persist_user(data)
