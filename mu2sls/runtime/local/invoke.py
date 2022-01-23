

## Synchronous local invocation.
## Simply find the method in the client and call it.
def SyncInvoke(client, method_name, *args):
    return getattr(client, method_name)(*args)

## TODO: Implement AsyncInvoke and wait