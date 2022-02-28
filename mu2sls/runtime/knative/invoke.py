import os
import requests

from uuid import uuid4

## This is an auxiliary function used to get the req_id and the ip
def get_ip_req_id(env):
    ## If env is None, then we are in a client, and therefore we need to generate
    ## a new identifier and find the ip from the environment
    if env is None:
        ip = os.environ.get('LOAD_BALANCER_IP')
        assert ip is not None
        req_id = str(uuid4())
        ## Actually, the knative request contains a request field in the headers, 
        ##   called: 'X-Request-Id'
        ## I am not sure if that is guaratneed to be the same per request.
        ##
        ## TODO: If we want to support client invocations through the standard
        ##       HTTP API, then we need to use the knative internal req_id
    else:
        ## Get the request_id from the environment
        req_id = env.instance_id

        ## Get the load balancer ip from the environment
        ip = env.load_balancer_ip
    return (ip, req_id)

def SyncInvoke(client: str, method_name: str, *args, env=None):
    
    ## Extract the ip, req_id from the environment or generate them
    ip, req_id = get_ip_req_id(env)

    client = client.lower()
    ## Note: This is obsolete. We are now passing data using json.
    # res = requests.get(f'http://{ip}/{method_name}', headers={"Host": f"{client}.default.example.com"},
    #                    params={"args": args}).json()
    res = requests.post(f'http://{ip}/{method_name}', 
                        headers={"Host": f"{client}.default.example.com"},
                        json={"args": args, "req_id": req_id}).json()
    return res

## TODO: Make that actual Async
def AsyncInvoke(client: str, method_name: str, *args, env=None):
    return SyncInvoke(client, method_name, *args, env=env)

def Wait(promise):
    return promise

def WaitAll(*promises):
    return promises
