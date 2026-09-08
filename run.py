"""Serving entry point.

The original ``run.py`` imported the Flask application and registered a
``@app.before_first_request`` hook that called ``db.create_all()``.  Flask's
``before_first_request`` has no FastAPI counterpart and was removed from Flask
itself, so the schema is created here at import time instead — the effect is the
same: the process that serves the API always finds its tables in place.

    uvicorn run:app
"""

import db
from app import app

db.create_all()

__all__ = ["app"]
