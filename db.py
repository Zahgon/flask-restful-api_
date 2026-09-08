"""Database access layer.

The original application used ``flask_sqlalchemy``: a single ``SQLAlchemy``
object owned the declarative base, the engine and a request scoped session, and
it was bound to the application through ``db.init_app(app)``.

FastAPI has no equivalent extension, so the same three responsibilities are
provided here with plain SQLAlchemy:

* ``Base``    - the declarative base every model inherits from.
* ``session`` - a ``scoped_session`` whose scope is one HTTP request.  The scope
  key lives in a :class:`~contextvars.ContextVar`, which Starlette copies into
  the worker thread it uses to run synchronous endpoints, so a request handler
  always sees its own session no matter which thread executes it.
* ``init_engine`` / ``create_all`` - the explicit replacements for
  ``db.init_app(app)`` and ``db.create_all()``.
"""

import os
from contextvars import ContextVar
from itertools import count

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

DEFAULT_DATABASE_URI = "sqlite:///data.db"

Base = declarative_base()

_session_factory = sessionmaker(autocommit=False, autoflush=False)

_request_scope = ContextVar("db_request_scope", default=0)
_scope_counter = count(1)


def _current_scope():
    """Scope key for :data:`session`; one distinct value per HTTP request."""
    return _request_scope.get()


session = scoped_session(_session_factory, scopefunc=_current_scope)

engine = None


def begin_request_scope():
    """Open a new session scope and return the token used to close it."""
    return _request_scope.set(next(_scope_counter))


def end_request_scope(token):
    """Discard the session opened for the scope identified by ``token``."""
    session.remove()
    _request_scope.reset(token)


def resolve_database_uri(database_uri, root_path):
    """Make a relative SQLite URI absolute against ``root_path``.

    ``flask_sqlalchemy`` resolved ``sqlite:///data.db`` against the Flask
    application's ``root_path``, which is the directory of the module that
    created the application.  Reproducing that here keeps the database files in
    the same two places the original put them: ``data.db`` next to ``app.py``
    for the served application and ``tests/data.db`` for the test suite.
    """
    prefix = "sqlite:///"
    if not database_uri.startswith(prefix):
        return database_uri
    path = database_uri[len(prefix) :]
    if not path or path.startswith("/") or path == ":memory:":
        return database_uri
    return prefix + os.path.join(root_path, path)


def init_engine(database_uri):
    """Create the engine and bind the session factory to it."""
    global engine
    connect_args = {}
    if database_uri.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    engine = create_engine(database_uri, connect_args=connect_args)
    _session_factory.configure(bind=engine)
    return engine


def create_all():
    """Create every table declared on :data:`Base`."""
    Base.metadata.create_all(bind=engine)


class SessionMiddleware:
    """Give every HTTP request its own session and discard it afterwards.

    This is the replacement for the application context teardown that
    ``flask_sqlalchemy`` installed to call ``session.remove()``.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        token = begin_request_scope()
        try:
            await self.app(scope, receive, send)
        finally:
            end_request_scope(token)
