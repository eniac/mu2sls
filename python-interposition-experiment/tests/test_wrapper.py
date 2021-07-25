import logging

from runtime import wrappers, beldi_stub

logging.basicConfig(level=logging.DEBUG)

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

    ## TODO: What is the correct key for a persistent object? It might be one per service? So maybe we should use the service name?
    collection_key = "test-collection"
    collection_init_val = []
    collection = wrappers.wrap_terminal(collection_key, collection_init_val, beldi)

    # print(dir(collection))
    
    # print(wrapped_collection.__repr__())
    # print(dir(wrapped_collection))

    collection.append(0)

    assert collection.index(0) == 0

    collection.append(1)
    assert collection.index(0) == 0
    assert collection.index(1) == 1

    el = collection.pop()
    assert el == 1
    assert collection.index(0) == 0

    el = collection.pop()
    assert el == 0

    assert collection + [5] == [5]

    collection += [5]
    assert collection.index(0) == 5

    el = collection.pop()
    assert el == 5

def test_counter():
    beldi = beldi_stub.Beldi()

    ## TODO: What is the correct key for a persistent object? It might be one per service? So maybe we should use the service name?
    counter_key = "test-counter"
    counter_init_val = Counter()
    counter = wrappers.wrap_terminal(counter_key, counter_init_val, beldi)

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

## TODO: For this test to pass, we need to wrap integers (and other primitives differently)
def test_int_counter():
    beldi = beldi_stub.Beldi()

    ## TODO: What is the correct key for a persistent object? It might be one per service? So maybe we should use the service name?
    counter_key = "test-int-counter"
    counter_init_val = 0
    counter = wrappers.wrap_terminal(counter_key, counter_init_val, beldi)

    print(counter + 1)
    assert counter == 0
    assert counter == 0

    counter += 1

    assert counter == 1
    assert counter == 1

    counter = 5

    assert counter == 5
    assert counter == 5

    counter = 4

    assert counter == 4
    assert counter == 4
