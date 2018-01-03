from mvc.api.wsgi import router
from mvc.api.controllers import persons


class APIRouter(router.Router):

    def _setup_routes(self, mapper):
        mapper.redirect("", "/")
        mapper.resource("person", "persons",
                        controller=persons.create_resource())
        return mapper
