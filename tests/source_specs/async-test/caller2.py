from uuid import uuid4

from compiler import decorators

@decorators.service
class Caller2(object):
    def __init__(self):
        pass

    async def req(self, value: int):
        
        p1 = AsyncInvoke('Backend', 'req', value)
        return await WaitAll(p1)