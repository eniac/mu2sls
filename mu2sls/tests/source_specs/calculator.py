from compiler import decorators

@decorators.service
class Calculator(object):
    def __init__(self):
        self.value = 0 # type: Persistent[int]

    def add(self, number):
        self.value += number

    def subtract(self, number):
        self.value -= number

    def get(self):
        ## TODO: There is a bug and when we return self.value, we return the WrapperTerminal instead of the actual value.
        return self.value

        ## TODO: This also doesn't work!
        # return self.value.__repr()