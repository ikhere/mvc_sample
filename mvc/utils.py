from functools import wraps
from jsonschema import Draft4Validator

from mvc.exceptions import InvalidInput


def validate(schema):
    validator = Draft4Validator(schema)

    def wrapper(fn):
        @wraps(fn)
        def wrapped(controller, *args, **kwargs):
            body = kwargs.get('body', {})
            errors = [err.message for err in validator.iter_errors(body)]
            if errors:
                raise InvalidInput(errors=errors)
            return fn(controller, *args, **kwargs)
        return wrapped

    return wrapper


def response_code(code):
    def wrapper(fn):
        fn.wsgi_code = code
        return fn
    return wrapper
