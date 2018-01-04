import ast

from functools import wraps
from jsonschema import Draft4Validator

from mvc import logger
from mvc.exceptions import InvalidInput

LOG = logger.get_logger(__name__)


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


def scrub_search_options(search_opts):
    for k, v in search_opts.items():
        try:
            search_opts[k] = ast.literal_eval(v)
        except (ValueError, SyntaxError):
            LOG.debug("Could not evaluate value %s, assuming string." % v)


def remove_invalid_filter_options(search_opts, allowed_options):
    bad_options = [opts for opts in search_opts.keys()
                   if opts not in allowed_options]
    LOG.debug("Removing options '%s' from query." % ', '.join(bad_options))
    for k in bad_options:
        del search_opts[k]
