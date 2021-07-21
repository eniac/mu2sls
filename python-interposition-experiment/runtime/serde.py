import pickle

def serialize(obj):
    return pickle.dumps(obj)

def deserialize(bin):
    return pickle.loads(bin)