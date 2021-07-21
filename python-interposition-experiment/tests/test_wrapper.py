from runtime import wrappers, beldi_stub


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