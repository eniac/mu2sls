import json

from runtime.beldi.common import *

def serialize(item):
    # print("Serialize:", item, "to:", json.dumps(item))
    ## TODO: There is a bug with this serialization :')
    ## It serializes keys to dictionaries as strings...
    ## TODO: We should use pickle, I don't know why we switched
    return json.dumps(item).encode()

def deserialize(bitem: bytes):
    decoded_string = bitem.decode()
    # print("Deserialized:", decoded_string, "to:", json.loads(decoded_string))
    return json.loads(decoded_string)


## Old way of doing serialization/deserialization

#import pickle

# def serialize(obj):
#     return pickle.dumps(obj)

# def deserialize(bin):
#     return pickle.loads(bin)