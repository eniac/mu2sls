from uuid import uuid4

from compiler import decorators

@decorators.service
class Caller(object):
    def __init__(self):
        self.val = [] # type: Persistent[list]

    async def compose(self, value: int):
        
        p1 = AsyncInvoke('Service1', 'set', value)
        p2 = AsyncInvoke('Service2', 'set', value)

        prev1, prev2 = await WaitAll(p1, p2)

        return (prev1, prev2)