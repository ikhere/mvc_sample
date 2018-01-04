import webob
import webob.exc
from webob.dec import wsgify

from mvc import exceptions, logger
from mvc.jsonify import dumps, loads

LOG = logger.get_logger(__name__)
CONTENT_TYPE = 'application/json'


class Request(webob.Request):
    def get_content_type(self):
        if "Content-Type" not in self.headers:
            return

        content_type = self.content_type

        if content_type != CONTENT_TYPE:
            raise exceptions.InvalidContentType(content_type=content_type)

        return content_type


class Response(object):
    def __init__(self, obj, code=None):
        self.obj = obj
        self._default_code = 200
        self._code = code

    @property
    def code(self):
        return self._code or self._default_code

    def serialize(self):
        response = webob.Response()
        response.status_int = self.code
        if self.obj is not None:
            body = dumps(self.obj)
            response.body = body
            response.content_type = CONTENT_TYPE
        return response


class ResourceExceptionHandler(object):
    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_val:
            return None

        if isinstance(exc_val, exceptions.InvalidInput):
            raise Fault(webob.exc.HTTPNotAcceptable(explanation=exc_val.msg,
                                                    detail=exc_val.errors))
        elif isinstance(exc_val, exceptions.NotFound):
            raise Fault(webob.exc.HTTPNotFound(explanation=exc_val.msg))
        elif isinstance(exc_val, exceptions.Invalid):
            raise Fault(webob.exc.HTTPBadRequest(explanation=exc_val.msg))

        return False


class Resource(object):

    def __init__(self, controller):
        self.controller = controller

    def get_body(self, request):
        if len(request.body) == 0:
            LOG.debug("Empty body provided in request")
            return None, ''

        try:
            content_type = request.get_content_type()
        except exceptions.InvalidContentType as ex:
            raise webob.exc.HTTPBadRequest(explanation=ex.msg)

        if not content_type:
            LOG.debug("No content-type provided in request")
            return None, ''

        return content_type, request.body

    def deserialize(self, body):
        try:
            body = loads(body)
        except ValueError:
            raise exceptions.MalformedRequestBody(
                reason='cannot understand JSON')
        return {'body': body}

    def get_action_args(self, request):
        try:
                args = request.environ['wsgiorg.routing_args'][1].copy()
        except KeyError:
            args = {}

        content_type, body = self.get_body(request)

        try:
            if content_type:
                contents = self.deserialize(body)
            else:
                contents = {}
        except exceptions.MalformedRequestBody as ex:
            raise webob.exc.HTTPBadRequest(explanation=ex.msg)

        try:
            del args['controller']
        except KeyError:
            pass

        args.update(contents)
        return args

    def get_action(self, action_args):
        action = action_args.pop('action')
        try:
            return getattr(self.controller, action)
        except AttributeError as ex:
            LOG.error("No action (%s) for controller (%s) Error: %s" %
                      (action, self.controller, ex))
            raise webob.exc.HTTPNotImplemented()

    def process_action(self, request, action_args):
        action = self.get_action(action_args)
        try:
            with ResourceExceptionHandler():
                action_result = action(request, **action_args)
        except Fault as ex:
            response = ex
        else:
            resp_obj = None
            if isinstance(action_result, dict) or action_result is None:
                resp_obj = Response(action_result)
            elif isinstance(action_result, Response):
                resp_obj = action_result
            if resp_obj:
                if hasattr(action, 'wsgi_code'):
                    resp_obj._default_code = action.wsgi_code
                response = resp_obj.serialize()
            else:
                response = action_result
        return response

    def process(self, request):
        action_args = self.get_action_args(request)
        response = self.process_action(request, action_args)
        return response

    @wsgify(RequestClass=Request)
    def __call__(self, request):
        LOG.debug("%(method)s: %(url)s" %
                  {'method': request.method, 'url': request.url})
        try:
            return self.process(request)
        except webob.exc.HTTPError as ex:
            LOG.error(ex)
            return Fault(ex)
        except Exception:
            LOG.exception("Caught unknown exception")
            return Fault(webob.exc.HTTPInternalServerError(
                explanation="Internal server error"))


class Fault(webob.exc.HTTPException):
    def __init__(self, exc):
        self.wrapped_exc = exc
        self.status_int = exc.status_int

    @wsgify(RequestClass=Request)
    def __call__(self, request):
        fault_body = {
            'code': self.status_int,
            'reason': self.wrapped_exc.explanation,
        }
        if hasattr(self.wrapped_exc, 'detail') and self.wrapped_exc.detail:
            fault_body['detail'] = self.wrapped_exc.detail
        fault_body = dumps(fault_body)
        self.wrapped_exc.body = fault_body
        self.wrapped_exc.content_type = 'application/json'
        return self.wrapped_exc

    def __str__(self):
        return str(self.wrapped_exc)
