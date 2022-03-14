from uuid import uuid4

from compiler import decorators
from runtime.transaction_exception import TransactionException


@decorators.service
class FrontendAbort(object):
    def __init__(self):
        self.val = [] # type: Persistent[list]

    ## We need to do that in a separate function due to a bug in uncompyle
    def handle_abort(self):
        print("Transaction was aborted, returning!")
        return list(self.val)

    def compose(self, value: int):
        
        try:
            BeginTx()
            prev1 = SyncInvoke('Service1', 'set', value)
            ## It is not clear what happens with assignments of persistent fields
            ## I don't think we want to allow them as they are, since they pass a reference
            ##
            ## We need to figure out if they pass a reference or a value, by default, I think that
            ## we want them to pass value.
            ##
            ## TODO: Figure that out
            # prev2 = int(self.val)
            # self.val = value
            self.val.append(value)
            new_val = list(self.val)
            prev3 = SyncInvoke('Service2', 'set', value)

            print(" -- Calling abort!")
            AbortTx()
            ret = (prev1, new_val, prev3)
        except TransactionException as e:
            return self.handle_abort()
        
        
        return ret

        ## We are here if the transaction failed
        # 
