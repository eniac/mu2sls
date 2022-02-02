import os
import requests

def SyncInvoke(client, method_name: str, *args):
    ip = os.environ.get('LOAD_BALANCER_IP')
    assert ip is not None
    res = requests.get(f'http://{ip}', headers={"Host": f"{client}.default.example.com"},
                       params=args).json()
    return res

def AsyncInvoke(client, method_name: str, *args):
    return SyncInvoke(client, method_name, *args)

def Wait(promise):
    return

def WaitAll(*promises):
    return