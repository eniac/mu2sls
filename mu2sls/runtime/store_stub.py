from runtime import beldi_stub

class Store:
    def __init__(self):
        pass
        # self.store = beldi_stub.Beldi()

    ## This method initializes the environment,
    ##   which is essential to invoke store methods.
    ##
    ## In the stub context it is not actually important.
    def init_env(self, name="default-store"):
        self.env = None
        self.name = name
        self.store = beldi_stub.Beldi(name)

    ## This implements a read method on the store
    ##
    ## Normally, this would also use the environment
    ## to perform the invocation
    def eos_read(self, key):
        return self.store.get(key)
    
    ## This implements a write method on the store
    ##
    ## Normally, this would also use the environment
    ## to perform the invocation
    def eos_write(self, key, value):
        return self.store.set(key, value)
    
    ## TODO: These are still empty and their APIs undecided.
    ##
    ## TODO: We need to implement them for Beldi
    def contains(self, key):
        return self.store.contains(key)
    
    def set_if_not_exists(self, key, value):
        return self.store.set_if_not_exists(key, value)

    def begin_tx(self):
        pass

    def end_tx(self):
        pass