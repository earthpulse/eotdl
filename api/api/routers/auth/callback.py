from fastapi import APIRouter

from .login import _code_store

router = APIRouter()


@router.get("/callback", name="callback", include_in_schema=False)
def callback(code: str = None, state: str = None):
    if not code or state not in _code_store:
        return "Invalid request", 400
    _code_store[state]["code"] = code
    return "Login successful! You may now close this window."
