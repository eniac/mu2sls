from compiler import decorators

@decorators.service
class Service:
    def __init__(self):
        self.collection = [] # type: Persistent[list]

    def test(self):
        print("Executing test method of service")
        self.collection.append(0)

        assert self.collection.index(0) == 0

        self.collection.append(1)
        assert self.collection.index(0) == 0
        assert self.collection.index(1) == 1

        el = self.collection.pop()
        assert el == 1
        assert self.collection.index(0) == 0

        el = self.collection.pop()
        assert el == 0

        assert self.collection + [5] == [5]

        self.collection = [1]
        assert self.collection.index(1) == 0

        self.collection += [5]
        assert self.collection.index(1) == 0
        assert self.collection.index(5) == 1

        el = self.collection.pop()
        assert el == 5

