from mvc import logger

from mvc.utils import validate
from mvc.utils import response_code

from mvc.api.wsgi.resource import Resource
from mvc.api.controllers.base import BaseController

LOG = logger.get_logger(__name__)

SCHEMA = {
    "type": "object",
    "required": ["person"],
    "properties": {
        "person": {
            "type": "object",
            "required": ["name"],
            "properties": {"name": {"type": "string", "maxLength": 250}}
        }
    }
}


class PersonController(BaseController):

    def index(self):
        persons = self.db.person_get_all()
        return {'persons': persons}

    def show(self, id):
        person = self.db.person_get(id)
        return {'person': person}

    @validate(SCHEMA)
    def create(self, body):
        LOG.info("Request to create person: %s" % body)
        create_values = body['person']
        person = self.db.person_create(create_values)
        return {'person': person}

    @validate(SCHEMA)
    def update(self, id, body):
        LOG.info("Request to update person '%s' : %s" % (id, body))
        update_values = body['person']
        person = self.db.person_update(id, update_values)
        return {'person': person}

    @response_code(204)
    def delete(self, id, body=None):
        LOG.info("Request to delete person '%s'" % id)
        self.db.person_delete(id)


def create_resource():
    return Resource(PersonController())
