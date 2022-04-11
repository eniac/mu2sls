import asyncio

from runtime import request_lib
from runtime.beldi import beldi
from runtime.beldi import common
from runtime.knative import invoke
from runtime.logger_abstraction import Logger
from runtime.transaction_exception import TransactionException


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
        res = super().SyncInvoke(client_name, method_name, *args)

        ## If the callee returns an abort response, then abort
        if request_lib.is_abort_response(res):
            print("Transaction was aborted by callee... aborting too")
            self.AbortTx()
        return res

    def AsyncInvoke(self, client_name: str, method_name: str, *args):
        self.env.increase_calls()
        if self.env.txn_id is not None:
            beldi.add_callee(self.env, client_name, method_name)
        beldi.log_invoke(self.env)
        res = super().AsyncInvoke(client_name, method_name, *args)

        return res

    async def Wait(self, promise):
        res = await super().Wait(promise)

        ## If the callee returns an abort response, then abort
        if request_lib.is_abort_response(res):
            print("Transaction was aborted by callee... aborting too")
            self.AbortTx()

        return res

    async def WaitAll(self, *promises):
        resps = await super().WaitAll(*promises)

        ## If the callee returns an abort response, then abort
        if any([request_lib.is_abort_response(res) for res in resps]):
            print("Transaction was aborted by callee... aborting too")
            self.AbortTx()
        return resps

    ## This implements a readand a write method on the store.
    ##
    ## It determines which read to use and how, depending on the environment,
    ## i.e., whether we are in a transaction.
    def read(self, key: str) -> tuple:
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

    def eos_write(self, key, value):
        return beldi.eos_write(self.env, key, value)

    def eos_contains(self, key):
        return beldi.eos_contains(self.env, key)

    def eos_set_if_not_exists(self, key, value):
        return beldi.eos_set_if_not_exist(self.env, key, value)

    def tpl_check_read(self, key):
        return beldi.tpl_check_read(self.env, key)

    def tpl_check_write(self, key, value):
        return beldi.tpl_check_write(self.env, key, value)

    def tpl_check_pop(self, key):
        return beldi.tpl_check_pop(self.env, key)

    def tpl_check_scan(self, key):
        return beldi.tpl_check_scan(self.env, key)

    def in_txn(self):
        return self.env.in_txn()

    def BeginTx(self):
        if beldi.ENABLE_TXN:
            return beldi.begin_tx(self.env)

    ## TODO: Hide async behind commit correctly
    # def CommitTx(self):
    #     ## TODO: This is not totally correct, we would normally want to
    #     ##       run it in the current running loop, but I am not
    #     ##       sure how to wait for it here then without having the
    #     ##       await keyword propagate in the whole application.
    #     eloop = asyncio.get_event_loop()
    #     eloop.run_until_complete(self._CommitTx())

    # def AbortTxNoExc(self):
    #     eloop = asyncio.get_event_loop()
    #     eloop.run_until_complete(self._AbortTxNoExc())

    def CommitTx(self):
        return self._CommitTx()

    def AbortTxNoExc(self):
        return self._AbortTxNoExc()

    # def CommitTx(self):
    #     return await self._CommitTx()

    # def AbortTxNoExc(self):
    #     return await self._AbortTxNoExc()

    ## TODO: Not sure why commit and abort have a different value
    def _inform_callees(self, callees, val):
        if len(callees) > 0:
            fs = []
            for client, method in callees:
                fs.append(self.AsyncInvoke(client, method, val))
            asyncio.create_task(self.WaitAll(*fs))

    def _CommitTx(self):
        if beldi.ENABLE_TXN:
            self.env.instruction = "COMMIT"
            callees = beldi.commit_tx(self.env)
            self._inform_callees(callees, "")
            self.env.txn_id = None
            self.env.instruction = None


    def _AbortTxNoExc(self):
        if beldi.ENABLE_TXN:
            self.env.instruction = "ABORT"
            callees = beldi.abort_tx(self.env)
            self._inform_callees(callees, {})
            self.env.txn_id = None
            self.env.instruction = None

    def AbortTx(self):
        if beldi.ENABLE_TXN:
            ## First call the Abort core
            self.AbortTxNoExc()

            ## Throw the transaction exception so that the user code can run
            ##   abort handler code.
            # print("Throwing abort exc!")
            raise TransactionException()

    ## This function checks the env (.instruction and .txn_id) and
    ## completes a transaction or aborts it.
    ##
    ## It is invoked by the request handler (in CompiledService)
    def commit_or_abort(self):
        if beldi.ENABLE_TXN:
            assert self.env.txn_id is not None
            if self.env.instruction == "COMMIT":
                self.CommitTx()
            elif self.env.instruction == "ABORT":
                ## We don't want to throw an exception when aborting due to a parent.
                self.AbortTxNoExc()
            else:
                assert False
            return {}
        else:
            return {}
