"""The ``POST /auth`` endpoint that ``flask_jwt`` used to register for us."""

import json

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from security import JWTError, authenticate, encode_token

router = APIRouter(tags=["auth"])

USERNAME_KEY = "username"
PASSWORD_KEY = "password"


@router.post("/auth")
async def auth_request(request: Request):
    raw_body = await request.body()
    try:
        data = json.loads(raw_body)
    except ValueError:
        data = None
    if not isinstance(data, dict):
        raise JWTError(
            "Bad Request",
            "The browser (or proxy) sent a request that this server could not "
            "understand.",
            status_code=400,
        )

    username = data.get(USERNAME_KEY, None)
    password = data.get(PASSWORD_KEY, None)
    criterion = [username, password, len(data) == 2]

    if not all(criterion):
        raise JWTError("Bad Request", "Invalid credentials")

    user = authenticate(username, password)
    if user:
        return JSONResponse(
            status_code=200, content={"access_token": encode_token(user)}
        )
    raise JWTError("Bad Request", "Invalid credentials")
