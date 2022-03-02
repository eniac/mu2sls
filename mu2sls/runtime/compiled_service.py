import json


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
    def apply_request(self, method_name: str, request) -> str:
        print("Request Headers:", dict(request.headers))
        request_json = request.get_json()
        print("Request JSON:", request_json)
        
        ## Set the environment based on the request
        self.logger.set_env(request_json)

        ## Check whether we should execute request or whether it should just
        ##   be committed or aborted.
        if self.logger.env.in_txn_commit_or_abort():
            print("Performing commit or abort!")
            ## If env.instruction is commit or abort, do that!
            ##
            ## In this case, the request might not even contain arguments
            return self.logger.commit_or_abort()
        else:
            print("Applying request")
            ret_val = getattr(self, method_name)(*(request_json['args']))
            return json.dumps(ret_val)
