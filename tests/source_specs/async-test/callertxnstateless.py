from uuid import uuid4

from compiler import decorators

@decorators.service
class CallerTxnStateless(object):
    def __init__(self):
        pass

    async def request(self, value: int):

        p1 = AsyncInvoke('EchoBackend1', 'request', value)
        p2 = AsyncInvoke('EchoBackend2', 'request', value)

        prev1, prev2 = await WaitAll(p1, p2)

        return (prev1, prev2)