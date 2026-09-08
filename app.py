"""FastAPI application.

This is the port of the original ``app.py``, which built a ``Flask`` object,
wrapped it in ``flask_restful.Api``, attached ``flask_jwt.JWT`` and
``flask_cors.CORS``, and registered nine resources.  The FastAPI equivalents are
an ``APIRouter`` per resource module, a ``CORSMiddleware``, a session middleware
that replaces ``flask_sqlalchemy``'s request scoped session, and the error
handlers in :mod:`errors` that keep the error payloads identical.

Like the original, importing this module does **not** create the database
schema; ``run.py`` does that.
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import db
from db import SessionMiddleware
from errors import register_error_handlers
from resources.auth import router as auth_router
from resources.balance import router as balance_router
from resources.item import router as item_router
from resources.item import welcome_router
from resources.pay import router as pay_router
from resources.store import router as store_router
from resources.user import router as user_router
from resources.user_info import router as user_info_router
from security import SECRET_KEY

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

CORS_HEADERS = "Content-Type"
SQLALCHEMY_DATABASE_URI = "sqlite:///data.db"

db.init_engine(db.resolve_database_uri(SQLALCHEMY_DATABASE_URI, ROOT_PATH))

app = FastAPI(
    title="flask-restful-api",
    description="REST API for a small store, ported from Flask to FastAPI.",
    version="0.1.0",
)
app.state.secret_key = SECRET_KEY

app.add_middleware(SessionMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=[CORS_HEADERS],
)

register_error_handlers(app)

app.include_router(store_router)
app.include_router(item_router)
app.include_router(user_router)
app.include_router(balance_router)
app.include_router(pay_router)
app.include_router(user_info_router)
app.include_router(auth_router)
app.include_router(welcome_router)
