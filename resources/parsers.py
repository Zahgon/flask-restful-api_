"""Request body models.

``flask_restful.reqparse`` declared one ``RequestParser`` per resource, each
argument carrying a ``help`` string that became the error message whenever the
argument was missing or could not be converted.  Its failure payload was::

    HTTP 400 {"message": {"<argument>": "<help text>"}}

FastAPI validates bodies with Pydantic instead, so every parser becomes a
:class:`RequestParser` subclass and the help strings travel with the fields.
:func:`reqparse_error_payload` renders a Pydantic validation error back into the
exact shape shown above.
"""

from pydantic import BaseModel, ConfigDict, Field

DEFAULT_HELP = (
    "Missing required parameter in the JSON body or the post body or the query string"
)


def parser_argument(help_text, **kwargs):
    """Declare a field the way ``parser.add_argument(..., help=...)`` did."""
    return Field(json_schema_extra={"help": help_text}, **kwargs)


class RequestParser(BaseModel):
    """Base class for the models that replace ``reqparse.RequestParser``.

    ``coerce_numbers_to_str`` reproduces ``type=str`` accepting a JSON number,
    and ``extra="ignore"`` reproduces reqparse discarding undeclared arguments.
    """

    model_config = ConfigDict(coerce_numbers_to_str=True, extra="ignore")

    @classmethod
    def help_texts(cls):
        return {
            name: (field.json_schema_extra or {}).get("help", DEFAULT_HELP)
            for name, field in cls.model_fields.items()
        }


def _known_help_texts():
    texts = {}
    pending = list(RequestParser.__subclasses__())
    while pending:
        parser = pending.pop()
        pending.extend(parser.__subclasses__())
        texts.update(parser.help_texts())
    return texts


def reqparse_error_payload(exc):
    """Render a Pydantic validation error the way reqparse rendered its own.

    reqparse aborted on the first offending argument, so only the first error is
    reported here as well.
    """
    texts = _known_help_texts()
    for error in exc.errors():
        location = [part for part in error["loc"] if part != "body"]
        if not location:
            continue
        argument = str(location[0])
        return {"message": {argument: texts.get(argument, DEFAULT_HELP)}}
    return {"message": DEFAULT_HELP}
