import json

def serialize(item):
    return json.dumps(item).encode()


def deserialize(bitem: bytes):
    return json.loads(bitem.decode())


## Old way of doing serialization/deserialization

#import pickle

# def serialize(obj):
#     return pickle.dumps(obj)

# def deserialize(bin):
#     return pickle.loads(bin)