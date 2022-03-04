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
    def __init__(self):
        self.invoke_lib = invoke

    ## This method initializes the environment,
    ##   which is essential to invoke store methods.
    ##
    ## In the stub context it is not actually important.
    def init_env(self, name="default-store", req_id=None):
        self.env = common.Env(name, req_id=req_id)

    ## Set the environment for this request using the request_json
    def set_env(self, request_json: dict):
        self.env.extract_request_metadata(request_json)

    def SyncInvoke(self, client_name: str, method_name: str, *args):
        self.env.increase_calls()
        if self.env.txn_id is not None:
            beldi.add_callee(self.env, client_name, method_name)
        beldi.log_invoke(self.env)
        return super().SyncInvoke(client_name, method_name, *args)

    def AsyncInvoke(self, client_name: str, method_name: str, *args):
        self.env.increase_calls()
        if self.env.txn_id is not None:
            beldi.add_callee(self.env, client_name, method_name)
        beldi.log_invoke(self.env)
        return super().AsyncInvoke(client_name, method_name, *args)

    ## This implements a readand a write method on the store.
    ##
    ## It determines which read to use and how, depending on the environment,
    ## i.e., whether we are in a transaction.
    def read(self, key: str) -> tuple[bool, object]:
        if self.env.in_txn():
            return beldi.tpl_read(self.env, key)
        else:
            return (True, beldi.eos_read(self.env, key))

    def write(self, key: str, value) -> bool:
        if self.env.in_txn():
            return beldi.tpl_write(self.env, key, value)
        else:
            beldi.eos_write(self.env, key, value)
            return True


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
        return beldi.eos_set_if_not_exists(self.env, key, value)

    def BeginTx(self):
        return beldi.begin_tx(self.env)
        
        ## TODO: We can optimize next gets/sets to the same object to not get again 
        ##       if they are in the same transaction, since we have already gotten and locked them.
        ##
        ##       Therefore, there is no need to get or set them before commiting. We can just keep
        ##       their version and run a set before the commit.

        ## TODO: Move that to the compiler
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

    def CommitTx(self):
        self.env.instruction = "COMMIT"
        callees = beldi.commit_tx(self.env)
        for client, method in callees:
            self.SyncInvoke(client, method, {})
        self.env.txn_id = None
        self.env.instruction = None

    def AbortTx(self):
        self.env.instruction = "ABORT"
        callees = beldi.abort_tx(self.env)
        for client, method in callees:
            self.SyncInvoke(client, method, {})
        self.env.txn_id = None
        self.env.instruction = None

    ## This function checks the env (.instruction and .txn_id) and
    ## completes a transaction or aborts it.
    ##
    ## It is invoked by the request handler (in CompiledService)
    def commit_or_abort(self):
        assert self.env.txn_id is not None
        if self.env.instruction == "COMMIT":
            self.commit_tx()
        elif self.env.instruction == "ABORT":
            self.abort_tx()
        else:
            assert False

