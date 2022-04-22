from typing import ValuesView
from uuid import uuid4

from compiler import decorators

@decorators.service
class EchoBackend1(object):
    def __init__(self):
        pass

    def request(self, value: int):
        return value