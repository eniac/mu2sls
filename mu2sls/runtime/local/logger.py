
##
## This is a class that does all logging locally (replacing Beldi)
##
## TODO: Move the following comment to the Logger superclass
##
## It currently implements a full API with all methods, but in the future,
## it would make sense to have it be agnostic to the actual API calls (invocation, store, etc)
##

from runtime import serde

from runtime.local import invoke

## TODO: Make a Logger abstraction, that contains everything that the store abstraction does
from runtime.logger_abstraction import Logger

class LocalLogger(Logger):
    ## TODO: @haoran It is not clear whether the name is supposed to be given at:
    ##       1. initialization/__init__ (called by deployment/context) 
    ##       2. init_env (called by the compiled service)
    ##       Also it is not clear if the Beldi initialization should also happen in (1) or (2)
    def __init__(self):
        self.invoke_lib = invoke
        # self.store = beldi_stub.Beldi()

    ## This method initializes the environment,
    ##   which is essential to invoke store methods.
    ##
    ## In the stub context it is not actually important.
    def init_env(self, name="default-store"):
        ## TODO: We can remove the env, since it is not needed by the local
        ##       logger.
        self.env = None
        self.name = name
        self.store = {}

    ## In the local version there is no need for tpl and eos read separation
    def read(self, key):
        return (True, self.eos_read(key))

    def write(self, key, value):
        self.eos_write(key, value)
        return True

    ## This implements a read method on the store
    ##
    ## Normally, this would also use the environment
    ## to perform the invocation
    def eos_read(self, key):
        try:
            serialized_val = self.store[key]
            return serde.deserialize(serialized_val)
        except:
            return ""
    
    ## This implements a write method on the store
    ##
    ## Normally, this would also use the environment
    ## to perform the invocation
    def eos_write(self, key, value):
        self.store[key] = serde.serialize(value)
    
    ## TODO: These are still empty and their APIs undecided.
    ##
    ## TODO: We need to implement them for Beldi
    def contains(self, key):
        return key in self.store
        
    def set_if_not_exists(self, key, value):
        self.BeginTx()
        if (not self.contains(key)):
            self.eos_write(key, value)
        self.CommitTx()

    ## TODO: Maybe we need to implement this differently
    def in_txn(self):
        return False

    def BeginTx(self):
        pass

    def CommitTx(self):
        pass    

    def AbortTx(self):
        pass        

    ## Invocations are inherited