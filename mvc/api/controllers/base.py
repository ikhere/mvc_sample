from mvc.db import api


class BaseController(object):
    def __init__(self):
        self.db = api
