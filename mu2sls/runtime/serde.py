import json

def serialize(item):
    return json.dumps(item).encode()

def deserialize(bitem: bytes):
    decoded_string = bitem.decode()
    ## json.loads() cannot handle an empty string,
    ##   so we make sure that we only pass a non-empty string to it
    if decoded_string == '':
        return None
    return json.loads(decoded_string)


## Old way of doing serialization/deserialization

#import pickle

# def serialize(obj):
#     return pickle.dumps(obj)

# def deserialize(bin):
#     return pickle.loads(bin)