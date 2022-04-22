from typing import ValuesView
from uuid import uuid4

from compiler import decorators

@decorators.service
class Backend1(object):
    def __init__(self):
        self.val = {} # type: Persistent[dict]

    def req(self, int_value: int):
        value = str(int_value)
        if value in self.val:
            # print("Value in dict")
            old_value = self.val[value]
            self.val[value] = old_value + 1
            ret = old_value
        else:
            # print("Value not in dict")
            self.val[value] = 1
            ret = 0

        return ret
