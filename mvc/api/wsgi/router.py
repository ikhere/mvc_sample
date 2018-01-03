import routes.middleware
import webob.exc

from mvc import logger
from routes import Mapper
from webob.dec import wsgify

LOG = logger.get_logger(__name__)


class Router(object):
    def __init__(self):
        mapper = Mapper()
        self._setup_routes(mapper)
        self._router = routes.middleware.RoutesMiddleware(
            self._dispatch, mapper)

    @classmethod
    def factory(cls):
        return cls()

    @wsgify()
    def __call__(self, req):
        return self._router

    @staticmethod
    @wsgify()
    def _dispatch(request):
        route = request.environ['wsgiorg.routing_args'][1]

        LOG.debug("Request '%(path)s' matched %(route)s" %
                  {'path': request.path, 'route': route})

        if not route:
            raise webob.exc.HTTPNotFound(
                explanation="No route matched for path '%s'" % request.path)

        app = route['controller']
        return app

    def _setup_routes(self, mapper):
        raise NotImplementedError()
