from uuid import uuid4

from compiler import decorators

from runtime.transaction_exception import TransactionException

@decorators.service
class Service2(object):
    def __init__(self):
        self.val = [] # type: Persistent[list]

    def set(self, value: int):
        # prev = int(self.val)
        # self.val = value
        self.val.append(value)
        new_val = list(self.val)

        return new_val
