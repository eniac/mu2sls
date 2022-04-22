from uuid import uuid4

from compiler import decorators

@decorators.service
class CallerStateless1(object):
    def __init__(self):
        pass

    async def request(self, value: int):
        
        p1 = AsyncInvoke('CallerStateless2', 'request', value)
        return await WaitAll(p1)