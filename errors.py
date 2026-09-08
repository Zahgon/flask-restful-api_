"""Error handlers that keep the HTTP error bodies identical to the Flask ones.

Three different Flask components produced three different error payloads:

* ``flask_jwt`` rendered ``{"status_code", "error", "description"}``.
* ``flask_restful.reqparse`` rendered ``{"message": {"<argument>": "<help>"}}``
  with status 400.
* ``flask_restful`` rendered ``{"message": "The method is not allowed for the
  requested URL."}`` with status 405.

FastAPI has its own defaults for all three, so each one is replaced here.
"""

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from resources.parsers import reqparse_error_payload
from security import JWTError


def handle_jwt_error(request, exc):
    """Render the JSON body ``flask_jwt`` produced for its own errors."""
    return JSONResponse(
        status_code=exc.status_code, content=exc.payload(), headers=exc.headers
    )


def handle_validation_error(request, exc):
    """Render the JSON body ``flask_restful.reqparse`` produced.

    A failure on a path parameter is not a body validation problem at all: in
    Werkzeug a value that does not satisfy the ``<int:...>`` converter simply
    fails to match the rule, so the request ends as a 404.
    """
    for error in exc.errors():
        if error["loc"] and error["loc"][0] == "path":
            return JSONResponse(status_code=404, content={"message": "Not Found"})
    return JSONResponse(status_code=400, content=reqparse_error_payload(exc))


def handle_http_exception(request, exc):
    """Match ``flask_restful``'s 405 body; leave every other status alone."""
    if exc.status_code == 405:
        return JSONResponse(
            status_code=405,
            content={"message": "The method is not allowed for the requested URL."},
            headers=getattr(exc, "headers", None),
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=getattr(exc, "headers", None),
    )


def register_error_handlers(app):
    app.add_exception_handler(JWTError, handle_jwt_error)
    app.add_exception_handler(RequestValidationError, handle_validation_error)
    app.add_exception_handler(StarletteHTTPException, handle_http_exception)
    return app
