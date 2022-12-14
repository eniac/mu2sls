from runtime.transaction_exception import TransactionException

##
## This is a Store class that is passed to services
## and supports a key-value store API.
##
class Logger:
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

    ## Clients initialization and getting
    def init_clients(self, clients={}):
        self.clients = clients

    def get_client(self, client_name: str):
        return self.clients[client_name]

    ##
    ## Invocations
    ##
    def SyncInvoke(self, client_name: str, method_name: str, *args):
        client = self.get_client(client_name)        
        return self.invoke_lib.SyncInvoke(client, method_name, env=self.env, *args)

    def AsyncInvoke(self, client_name: str, method_name: str, *args):
        client = self.get_client(client_name)
        return self.invoke_lib.AsyncInvoke(client, method_name, env=self.env, *args)

    async def Wait(self, promise):
        return await self.invoke_lib.Wait(promise)

    async def WaitAll(self, *promises):
        return await self.invoke_lib.WaitAll(*promises)

    ## The store should certainly implement these, and then determine whether to call
    ## tpl_read, or eos_read based on its current transaction status.
    ##
    ## Note: By default in our case there should never be an EOS read, since that would create
    ##       issues with transactions that run at the same time.
    def read(self, key):
        return None

    def write(self, key, value):
        return None

    ## This function repeats a transaction start until it manages to read from a key and lock it.
    def read_until_success(self, key: str):
        self.BeginTx()
        read_succeeded, ret = self.read(key)
        # print("Read for key:", key, "succeeded:", read_succeeded, "and returned value:", ret)
        while not read_succeeded:
            self.AbortTxNoExc()
            # self.AbortTx()
            self.BeginTx()
            read_succeeded, ret = self.read(key)
        return ret

    ## This function repeats a transaction start until it manages to read from a key and lock it.
    def read_throw(self, key: str):
        read_succeeded, ret = self.read(key)
        if not read_succeeded:
            ## This also throws an exception
            self.AbortTx()
            # raise TransactionException()
        else:
            return ret

    ## Only used by custom implementations
    def write_until_success(self, key: str, val):
        self.BeginTx()
        write_succeeded = self.write(key, val)
        # print("Write for key:", key, "with value:", val, "succeeded:", write_succeeded)
        while not write_succeeded:
            self.AbortTxNoExc()
            # self.AbortTx()
            self.BeginTx()
            write_succeeded = self.write(key, val)
        
    def write_throw(self, key: str, value):
        write_succeeded = self.write(key, value)
        if not write_succeeded:
            ## This also throws an exception
            self.AbortTx()
            # raise TransactionException()

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
    
    def eos_contains(self, key):
        return None
    
    ## This implements an atomic add if not exists
    def eos_set_if_not_exists(self, key, value):
        return None

    def BeginTx(self):
        return None

    def CommitTx(self):
        return None
    
    def AbortTx(self):
        return None

    