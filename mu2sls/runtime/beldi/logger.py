from uuid import uuid4
from runtime.beldi import beldi
from runtime.beldi import common

from runtime.knative import invoke

from runtime.logger_abstraction import Logger

##
## This is a logger class (similar to local.logger) that provides an idempotent API
## for a store, with calls, and transactions.
##
class BeldiLogger(Logger):
    ## TODO: @haoran It is not clear whether the name is supposed to be given at:
    ##       1. initialization/__init__ (called by deployment/context) 
    ##       2. init_env (called by the compiled service)
    ##       Also it is not clear if the Beldi initialization should also happen in (1) or (2)
    def __init__(self):
        self.invoke_lib = invoke

    ## This method initializes the environment,
    ##   which is essential to invoke store methods.
    ##
    ## In the stub context it is not actually important.
    def init_env(self, name="default-store", req_id=None):
        self.env = common.Env(name, req_id=req_id)

    def reinit_env(self, name, req_id):
        ## TODO: Make that not reinitialize everything for efficiency
        self.env = common.Env(name, req_id=req_id)

    def SyncInvoke(self, client_name: str, method_name: str, *args):
        self.env.increase_calls()
        return super().SyncInvoke(client_name, method_name, *args)

    def AsyncInvoke(self, client_name: str, method_name: str, *args):
        self.env.increase_calls()
        return super().AsyncInvoke(client_name, method_name, *args)

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

    ## TODO: Transfer with invocation
    ## - req_id
    ## - env.txn_id = env.instance_id
    ## - env.instruction = "EXECUTE"

    ## TODO: Check in callee if we are in non-execute in a transaction
    ##       do special work
    ##
    ## if not get_json()['instruction'] == "EXECUTE":
    ##     run_commit_abort_code

    ## TODO: Instance per concurrent worker/thread.
    ##       Put differently, no instance should be shared between 
    ##       two concurrent threads.
    ##
    ## The naive and straightforward way to do it, is to create
    ## a new instance per request. We should do that, and in the
    ## future, we can only reinitialize the environment per request,
    ## and have a read-only instance initialized once at the start.

    # dictionary = {thread_name: instance for thread_name in thread_names}

    ## TODO: Actually implement that
    def begin_tx(self):
        pass
        
        # cond = True
        # while cond:
        #     beldi.begin_txn(self.env)

        #     cond, ret = beldi.tpl_read(self.env, "key")

        #     if cond is False:
        #         beldi.abort_txn(self.env)

        
        # ret.update()

        # cond = beldi.tpl_write(self.env, "key", ret)
        # assert cond is True

        # beldi.commit_txn(self.env)

    def commit_tx(self):
        pass

    def abort_tx(self):
        pass
