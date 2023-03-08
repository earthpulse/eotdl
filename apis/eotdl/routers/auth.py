from fastapi.exceptions import HTTPException
from fastapi import Depends, APIRouter, status, Request

from fastapi.security import HTTPBearer, APIKeyHeader
from starlette.responses import RedirectResponse

from src.models import User
from src.usecases.user import persist_user
from src.usecases.auth import generate_login_url, generate_id_token, parse_token, generate_logout_url

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

token_auth_scheme = HTTPBearer(auto_error=False)
api_key_auth_scheme = APIKeyHeader(name='X-API-Key', auto_error=False)

@router.get("/login")
async def login(request: Request, goto: str = None):
    try:
        redirect_uri = request.url_for('callback')
        login_url = generate_login_url(redirect_uri, goto)
        return {"login_url": login_url}
    except Exception as e:
        print('ERROR', str(e))
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/callback", include_in_schema=False)
async def callback(request: Request, code: str, goto: str = None):
    try:
        redirect_uri = request.url_for('me')
        token = generate_id_token(code, redirect_uri)
        if goto:
            return RedirectResponse(url=f'{goto}?id_token={token}')
        return {'id_token': token}
    except Exception as e:
        print('ERROR', str(e))
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e))


def get_current_user(token: str = Depends(token_auth_scheme)):
    if not token:
        return None
    try:
        payload = parse_token(token.credentials)
        data = {
            'uid': payload['sub'],
            'name': payload['name'],
            'email': payload['email'],
            'picture': payload['picture'],
        }
        return persist_user(data)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/me")
async def me(user: User = Depends(get_current_user)):
    try:
        return user
    except Exception as e:
        print('ERROR', str(e))
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/logout")
async def logout(request: Request, redirect_uri: str = None):
    try:
        if redirect_uri is None:
            redirect_uri = request.url_for('home')
        logout_url = generate_logout_url(redirect_uri)
        return {"logout_url": logout_url}
    except Exception as e:
        print('ERROR', str(e))
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e))