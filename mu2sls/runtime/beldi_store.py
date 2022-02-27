from runtime.beldi import beldi
from runtime.beldi import common

from runtime.store_abstraction import Store

class BeldiStore(Store):
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
        self.env = common.Env(name)
        self.name = name

    ## This implements a read method on the store
    ##
    ## Normally, this would also use the environment
    ## to perform the invocation
    def eos_read(self, key):
        return beldi.eos_read(self.env, key)
    
    ## This implements a write method on the store
    ##
    ## Normally, this would also use the environment
    ## to perform the invocation
    def eos_write(self, key, value):
        return beldi.eos_write(self.env, key, value)
    
    ## TODO: These are still empty and their APIs undecided.
    ##
    ## TODO: We need to implement them for Beldi
    def contains(self, key):
        return beldi.eos_contains(self.env, key)
    
    ## TODO: @Haoran my goal was for this to be atomic. Maybe we need to either remove it
    ##       or wrap it with some lock.
    def set_if_not_exists(self, key, value):
        if not self.contains(key):
            self.eos_write(key, value)

    def begin_tx(self):
        pass

    def end_tx(self):
        pass
