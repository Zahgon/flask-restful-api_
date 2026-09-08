# Third party modules
import os

import pytest

# First party modules
from fastapi import FastAPI
from starlette.testclient import TestClient

import db
from db import SessionMiddleware
from errors import register_error_handlers
from resources.auth import router as auth_router
from resources.balance import router as balance_router
from resources.item import router as item_router
from resources.pay import router as pay_router
from resources.store import router as store_router
from resources.user import router as user_router
from resources.user_info import router as user_info_router

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

SQLALCHEMY_DATABASE_URI = "sqlite:///data.db"


def create_app():
    app = FastAPI()
    app.add_middleware(SessionMiddleware)
    register_error_handlers(app)

    app.include_router(auth_router)  # /auth

    app.include_router(store_router)  # /store/{name} and /stores
    app.include_router(item_router)  # /item/{name} and /items
    app.include_router(user_router)  # /register
    app.include_router(balance_router)  # /balance/{uuid}
    app.include_router(pay_router)  # /pay/{uuid}
    app.include_router(user_info_router)  # /user_info/{uuid}
    return app


@pytest.fixture
def client():
    app = create_app()

    db.init_engine(db.resolve_database_uri(SQLALCHEMY_DATABASE_URI, ROOT_PATH))
    db.create_all()

    with TestClient(app) as client:
        yield client
