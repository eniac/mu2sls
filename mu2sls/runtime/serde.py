import json

from runtime.beldi.common import *

def serialize(item):
    return json.dumps(item).encode()

def deserialize(bitem: bytes):
    decoded_string = bitem.decode()
    return json.loads(decoded_string)


## Old way of doing serialization/deserialization

#import pickle

# def serialize(obj):
#     return pickle.dumps(obj)

# def deserialize(bin):
#     return pickle.loads(bin)