import logging

from runtime import wrappers, beldi_stub

logging.basicConfig(level=logging.WARNING)

class Counter:
    def __init__(self):
        self.value = 0

    def get(self):
        return self.value
    
    def set(self, value):
        self.value = value

    def increment(self):
        self.value += 1

def test_list():
    ## Initialize a beldi_stub instance
    beldi = beldi_stub.Beldi()
    collection = []

    # print(dir(collection))

    wrapped_collection = wrappers.wrap_terminal(collection, beldi)

    
    # print(wrapped_collection.__repr__())
    # print(dir(wrapped_collection))

    wrapped_collection.append(0)

    assert wrapped_collection.index(0) == 0

    wrapped_collection.append(1)
    assert wrapped_collection.index(0) == 0
    assert wrapped_collection.index(1) == 1

    el = wrapped_collection.pop()
    assert el == 1
    assert wrapped_collection.index(0) == 0

    el = wrapped_collection.pop()
    assert el == 0

def test_counter():
    beldi = beldi_stub.Beldi()

    prewrapped_counter = Counter()
    counter = wrappers.wrap_terminal(prewrapped_counter, beldi)

    assert counter.value == 0
    assert counter.get() == 0

    counter.increment()

    assert counter.value == 1
    assert counter.get() == 1

    counter.set(5)

    assert counter.value == 5
    assert counter.get() == 5

    counter.value = 4

    assert counter.value == 4
    assert counter.get() == 4