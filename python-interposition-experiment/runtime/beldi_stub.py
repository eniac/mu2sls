
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