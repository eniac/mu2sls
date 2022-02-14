import os
import requests

def SyncInvoke(client, method_name: str, *args):
    ip = os.environ.get('LOAD_BALANCER_IP')
    assert ip is not None
    client = client.lower()
    res = requests.get(f'http://{ip}/{method_name}', headers={"Host": f"{client}.default.example.com"},
                       params={"args": args}).json()
    # res = requests.get(f'http://127.0.0.1:5000/{method_name}', params={"args": args}).json()
    return res

def AsyncInvoke(client, method_name: str, *args):
    return SyncInvoke(client, method_name, *args)

def Wait(promise):
    return

def WaitAll(*promises):
    return