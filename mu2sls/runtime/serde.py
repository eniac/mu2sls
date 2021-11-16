import pickle

## TODO: Consider replacing this with the same serde that Beldi does
##       to avoid divergence.

def serialize(obj):
    return pickle.dumps(obj)

def deserialize(bin):
    return pickle.loads(bin)