import json

from runtime.beldi.common import *

@log_timer("serialize")
def serialize(item):
    return json.dumps(item).encode()

@log_timer("deserialize")
def deserialize(bitem: bytes):
    decoded_string = bitem.decode()
    ## json.loads() cannot handle an empty string,
    ##   so we make sure that we only pass a non-empty string to it
    ##
    ## TODO: This might actually not be necessary...
    if decoded_string == '':
        return None
    return json.loads(decoded_string)


## Old way of doing serialization/deserialization

#import pickle

# def serialize(obj):
#     return pickle.dumps(obj)

# def deserialize(bin):
#     return pickle.loads(bin)