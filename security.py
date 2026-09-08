"""Authentication.

``flask_jwt`` supplied three things the application depended on: the
``POST /auth`` endpoint, the ``@jwt_required()`` decorator, and a JSON error
body of the form ``{"status_code", "error", "description"}``.  The extension is
unmaintained and Flask-only, so its behaviour is reproduced here on top of
``PyJWT`` and exposed to FastAPI as a dependency.

Every default it relied on is spelled out below, so the tokens minted here are
byte-compatible with the ones the Flask application minted.
"""

import hmac
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import Header

from models.user import UserModel

SECRET_KEY = "jose"
JWT_ALGORITHM = "HS256"
JWT_AUTH_HEADER_PREFIX = "JWT"
JWT_LEEWAY = timedelta(seconds=10)
JWT_EXPIRATION_DELTA = timedelta(seconds=300)
JWT_NOT_BEFORE_DELTA = timedelta(seconds=0)
JWT_REQUIRED_CLAIMS = ["exp", "iat", "nbf"]


class JWTError(Exception):
    """The error ``flask_jwt`` raised, with the same rendered JSON body."""

    def __init__(self, error, description, status_code=401, headers=None):
        self.error = error
        self.description = description
        self.status_code = status_code
        self.headers = headers or {}

    def payload(self):
        return {
            "status_code": self.status_code,
            "error": self.error,
            "description": self.description,
        }


def authenticate(username, password):
    user = UserModel.find_by_username(username)
    if user and hmac.compare_digest(user.password, password):
        return user


def identity(payload):
    user_id = payload["identity"]
    return UserModel.find_by_id(user_id)


def jwt_payload(user):
    """The claim set ``flask_jwt`` put in every token."""
    issued_at = datetime.utcnow()
    return {
        "exp": issued_at + JWT_EXPIRATION_DELTA,
        "iat": issued_at,
        "nbf": issued_at + JWT_NOT_BEFORE_DELTA,
        "identity": user.id,
    }


def encode_token(user):
    return jwt.encode(jwt_payload(user), SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_token(token):
    options = {"require": list(JWT_REQUIRED_CLAIMS)}
    return jwt.decode(
        token,
        SECRET_KEY,
        options=options,
        algorithms=[JWT_ALGORITHM],
        leeway=JWT_LEEWAY,
    )


def read_authorization_header(authorization):
    """Extract the token, reproducing ``flask_jwt``'s header parsing."""
    if not authorization:
        return None
    parts = authorization.split()
    if parts[0].lower() != JWT_AUTH_HEADER_PREFIX.lower():
        raise JWTError("Invalid JWT header", "Unsupported authorization type")
    elif len(parts) == 1:
        raise JWTError("Invalid JWT header", "Token missing")
    elif len(parts) > 2:
        raise JWTError("Invalid JWT header", "Token contains spaces")
    return parts[1]


def jwt_required(authorization: Optional[str] = Header(default=None)):
    """FastAPI dependency replacing ``@jwt_required()``.

    Returns the authenticated user, which the ported resources receive as
    ``current_identity`` exactly as ``flask_jwt.current_identity`` provided it.
    """
    token = read_authorization_header(authorization)
    if token is None:
        raise JWTError(
            "Authorization Required",
            "Request does not contain an access token",
            headers={"WWW-Authenticate": 'JWT realm="Login Required"'},
        )
    try:
        payload = decode_token(token)
    except jwt.InvalidTokenError as error:
        raise JWTError("Invalid token", str(error))

    current_identity = identity(payload)
    if current_identity is None:
        raise JWTError("Invalid JWT", "User does not exist")
    return current_identity
