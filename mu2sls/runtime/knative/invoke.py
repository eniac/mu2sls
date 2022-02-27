import os
import requests

def SyncInvoke(client: str, method_name: str, *args):
    ip = os.environ.get('LOAD_BALANCER_IP')
    assert ip is not None
    client = client.lower()
    ## Note: This is obsolete. We are now passing data using json.
    # res = requests.get(f'http://{ip}/{method_name}', headers={"Host": f"{client}.default.example.com"},
    #                    params={"args": args}).json()
    res = requests.post(f'http://{ip}/{method_name}', 
                        headers={"Host": f"{client}.default.example.com"},
                        json={"args": args}).json()
    return res

## TODO: Make that actual Async
def AsyncInvoke(client: str, method_name: str, *args):
    return SyncInvoke(client, method_name, *args)

def Wait(promise):
    return promise

def WaitAll(*promises):
    return promises