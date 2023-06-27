from fastapi.exceptions import HTTPException
from fastapi import Depends, APIRouter, status, Request
from pydantic import BaseModel
from fastapi.security import HTTPBearer, APIKeyHeader
import logging
import os

from ..src.models import User
from ..src.usecases.user import (
    persist_user,
    update_user,
    retrieve_user,
)
from ..src.usecases.auth import (
    generate_login_url,
    generate_id_token,
    parse_token,
    generate_logout_url,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

token_auth_scheme = HTTPBearer(auto_error=False)
api_key_auth_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)


@router.get("/login")
def login():
    try:
        return generate_login_url()
    except Exception as e:
        logger.exception("login")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/token")
def token(code: str):
    try:
        return generate_id_token(code)
    except Exception as e:
        logger.exception("token")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


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


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    try:
        print("ieeepa")
        return retrieve_user(user)
    except Exception as e:
        logger.exception("me")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/callback", name="callback", include_in_schema=False)
def logout_callback():
    return "You are logged out."


@router.get("/logout")
def logout(request: Request, redirect_uri: str = None):
    try:
        if redirect_uri is None:
            redirect_uri = str(request.url_for("callback"))
        logout_url = generate_logout_url(redirect_uri)
        return {"logout_url": logout_url}
    except Exception as e:
        logger.exception("logout")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


class UpdateData(BaseModel):
    name: str


@router.post("", include_in_schema=False)
def update_user_data(
    data: UpdateData,
    user: User = Depends(get_current_user),
):
    try:
        return update_user(user, data)
    except Exception as e:
        logger.exception("auth.update")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
