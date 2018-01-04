import six

from mvc import logger

LOG = logger.get_logger(__name__)


class MVCException(Exception):
    message = "An unknown exception occurred."
    code = 500

    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs
        self.kwargs['message'] = message

        for k, v in self.kwargs.items():
            if isinstance(v, Exception):
                self.kwargs[k] = six.text_type(v)

        if self._should_format():
            try:
                message = self.message % self.kwargs
            except Exception:
                LOG.exception("Failed while formatting exception message")
                message = self.message
        elif isinstance(message, Exception):
            message = six.text_type(message)

        self.msg = message
        super(MVCException, self).__init__(message)

    def _should_format(self):
        return self.kwargs['message'] is None or '%(message)s' in self.message

    def __unicode__(self):
        return six.text_type(self.msg)


class Invalid(MVCException):
    message = "Unacceptable parameters."
    code = 400


class NotFound(MVCException):
    message = "Not found."
    code = 404


class InvalidContentType(Invalid):
    message = "Invalid content type %(content_type)s."


class MalformedRequestBody(Invalid):
    message = "Malformed request body %(reason)s."


class InvalidInput(Invalid):
    message = "Invalid input."
    code = 406
    errors = None

    def __init__(self, errors=None, **kwargs):
        self.errors = errors
        super(InvalidInput, self).__init__(**kwargs)


class InvalidFilterValue(Invalid):
    message = "Invalid filter value '%(value)s'."


class PersonNotFound(NotFound):
    message = "Person '%(reference)s' not found."
