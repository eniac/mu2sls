from uuid import uuid4

from runtime.transaction_exception import TransactionException
from compiler import decorators

@decorators.service
class CallerTxn(object):
    def __init__(self):
        pass

    async def req(self, value: int):

        i = 0
        retry = True
        while retry:
            # print("Trying to perform transaction:", i)
            i += 1
            try:
                BeginTx()        
                p1 = AsyncInvoke('Backend1', 'req', value)
                p2 = AsyncInvoke('Backend2', 'req', value)

                ret = await WaitAll(p1, p2)
                CommitTx()
                retry = False
            except TransactionException as e:
                retry = True

        print("Transaction took", i, "tries")
        return ret
