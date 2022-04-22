import time
import logging
from compiler import decorators

@decorators.service
class Text:
    def __init__(self):
        pass

    async def upload_text(self, req_id, text):
        start = time.perf_counter_ns()
        promise = AsyncInvoke('ComposeReview', "upload_text", req_id, text)
        await Wait(promise)
        end = time.perf_counter_ns()
        duration = (end - start) / 1000000
        logging.error(f'APP Text.upload_text: {duration}')
