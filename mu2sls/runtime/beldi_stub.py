
import logging

from runtime import serde
from runtime import beldi

##
## This is a simple class that contains empty stubs for all beldi calls (for testing)
##

## Serialization happens in here

## Maybe have a Beldi Superclass
class Beldi:
    def __init__(self, name):
        self.name = name
        self.store = {}

    def begin_tx(self):
        pass

    def end_tx(self):
        pass

    def get(self, key: str):
        try:
            serialized_val = self.store[key]
            return serde.deserialize(serialized_val)
        except:
            return None
    
    def set(self, key: str, value):
        self.store[key] = serde.serialize(value)
    
    def contains(self, key: str):
        return key in self.store

    def set_if_not_exists(self, key: str , value):
        self.begin_tx()
        if (not self.contains(key)):
            self.set(key, value)
        self.end_tx()
