from typing import ValuesView
from uuid import uuid4

from runtime.transaction_exception import TransactionException
from compiler import decorators

@decorators.service
class Backend(object):
    def __init__(self):
        self.val = {} # type: Persistent[dict]

    def req(self, int_value: int):
        
        ## TODO: This is due to a bug in json serialization.
        ##       Make this proper again when we change to picke...
        value = str(int_value)

        retry = True
        while retry:
            try:
                BeginTx()
                if value in self.val:
                    # print("Value in dict")
                    old_value = self.val[value]
                    self.val[value] = old_value + 1
                    ret = old_value
                else:
                    # print("Value not in dict")
                    self.val[value] = 1
                    ret = 0
                CommitTx()
                retry = False
            except TransactionException as e:
                AbortTx()
                retry = True

        return ret