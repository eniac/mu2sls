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
        print(request)
        print(dict(request.headers))
        request_json = request.get_json()
        print(request_json)
        
        self.logger.set_env(request_json)

        ## TODO: If env.instruction is commit or abort, do that!
    
        ret_val = getattr(self, method_name)(*(request_json['args']))
        return json.dumps(ret_val)