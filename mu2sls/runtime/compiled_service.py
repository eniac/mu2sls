import asyncio
import json
import logging

from runtime.transaction_exception import TransactionException
from runtime import request_lib


## TODO: These methods needs to be prefixed with mu2sls or something to not clash with user-defined ones
class CompiledService:
    def __init__(self, logger):
        logger.init_env()
        self.logger = logger

    def init_clients(self, clients={}):
        self.logger.init_clients(clients)

    ## TODO: This one is specific to knative and maybe should be moved to a KnativeCompiledService object
    ##
    ## Set the environment for the new request
    async def apply_request(self, method_name: str, request) -> str:
        logging.error("-" * 20)
        # print("Request Headers:", dict(request.headers))
        request_json = await request.get_json()
        # print("Request JSON:", request_json)
        
        ## Set the environment based on the request
        self.logger.set_env(request_json)

        ## Initialize the persistent objects now that we have the environment
        self.__init_per_objects__()

        ## Check whether we should execute request or whether it should just
        ##   be committed or aborted.
        if self.logger.env.in_txn_commit_or_abort():
            # print("Performing commit or abort!")
            ## If env.instruction is commit or abort, do that!
            ##
            ## In this case, the request might not even contain arguments
            return self.logger.commit_or_abort()
        else:
            # print("Applying request")
            ## Catch Transaction exceptions and carefully return them to the user
            try:
                func = getattr(self, method_name)
                ret_val = func(*(request_json['args']))
                if asyncio.iscoroutinefunction(func):
                    ret_val = await ret_val
                return json.dumps(ret_val)
            except TransactionException as e:
                return json.dumps(request_lib.abort_response())
            
