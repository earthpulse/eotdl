from fastapi.exceptions import HTTPException
from fastapi import Depends, APIRouter
from fastapi.security import HTTPBearer, APIKeyHeader
import logging
import os

from ...src.usecases.user import persist_user
from ...src.usecases.auth import parse_token

logger = logging.getLogger(__name__)

token_auth_scheme = HTTPBearer(auto_error=False)
api_key_auth_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)

def key_auth(api_key: str = Depends(api_key_auth_scheme)):
    if not api_key or api_key != os.environ.get("ADMIN_API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return


# def token_auth(token: str = Depends(token_auth_scheme)):
def get_current_user(token: str = Depends(token_auth_scheme)):
    if not token:
        return None
    try:
        data = parse_token(token.credentials)
        return persist_user(data)
    except Exception as e:
        logger.exception("get_current_user")
        raise HTTPException(status_code=401, detail="Invalid token")


# async def get_current_user(api_key_user=Depends(key_auth), token_user=Depends(token_auth)):
#     if not token_user:
#         raise HTTPException(status_code=401, detail="Not authenticated")
#     return token_user











