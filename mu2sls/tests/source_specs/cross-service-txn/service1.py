from uuid import uuid4

from compiler import decorators

@decorators.service
class Service1(object):
    def __init__(self):
        self.val = 0 # type: Persistent[int]

    def set(self, value: int):
        prev = int(self.val)
        self.val = value

        return prev