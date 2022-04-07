import time
import logging
from uuid import uuid4

from compiler import decorators

@decorators.service
class UniqueId:
    def __init__(self):
        pass

    async def upload_unique_id(self, req_id):
        start = time.perf_counter_ns()
        review_id = str(uuid4())
        promise = AsyncInvoke('ComposeReview', "upload_unique_id", req_id, review_id)
        await Wait(promise)
        end = time.perf_counter_ns()
        duration = (end - start) / 1000000
        logging.error(f'APP UniqueId.upload_unique_id: {duration}')
