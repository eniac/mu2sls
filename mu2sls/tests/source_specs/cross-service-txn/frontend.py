from uuid import uuid4

from compiler import decorators

@decorators.service
class Frontend(object):
    def __init__(self):
        self.val = 0 # type: Persistent[int]

    def compose(self, value: int):
        
        BeginTx()
        prev1 = SyncInvoke('Service1', 'set', value)
        ## It is not clear what happens with assignments of persistent fields
        ## I don't think we want to allow them as they are, since they pass a reference
        ##
        ## We need to figure out if they pass a reference or a value, by default, I think that
        ## we want them to pass value.
        ##
        ## TODO: Figure that out
        prev2 = int(self.val)
        self.val = value
        prev3 = SyncInvoke('Service2', 'set', value)
        CommitTx()

        return (prev1, prev2, prev3)