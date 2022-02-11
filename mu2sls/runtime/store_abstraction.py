
##
## This is a Store class that is passed to services
## and supports a key-value store API.
##
class Store:
    ## TODO: @haoran It is not clear whether the name is supposed to be given at:
    ##       1. initialization/__init__ (called by deployment/context) 
    ##       2. init_env (called by the compiled service)
    ##       Also it is not clear if the Beldi initialization should also happen in (1) or (2)
    def __init__(self):
        pass

    ## This method initializes the environment,
    ##   which is essential to invoke store methods.
    ##
    ## In the stub context it is not actually important.
    def init_env(self, name="default-store"):
        self.env = None
        self.name = name

    ## This implements a read method on the store
    ##
    ## Normally, this would also use the environment
    ## to perform the invocation
    def eos_read(self, key):
        return None
    
    ## This implements a write method on the store
    ##
    ## Normally, this would also use the environment
    ## to perform the invocation
    def eos_write(self, key, value):
        return None
    
    def contains(self, key):
        return None
    
    ## This implements an atomic add if not exists
    def set_if_not_exists(self, key, value):
        return None

    def begin_tx(self):
        return None

    def end_tx(self):
        return None