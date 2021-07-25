
##
## This is a simple class that contains empty stubs for all beldi calls (for testing)
##

## Maybe have a Beldi Superclass
class Beldi:
    def __init__(self):
        self.store = {}

    def begin_tx(self):
        pass

    def end_tx(self):
        pass

    def get(self, key):
        try:
            return self.store[key]
        except:
            return None
    
    def set(self, key, value):
        self.store[key] = value
    
    def contains(self, key):
        return key in self.store

    def set_if_not_exists(self, key, value):
        self.begin_tx()
        if (not self.contains(key)):
            self.set(key, value)
        self.end_tx()
