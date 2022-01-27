from uuid import uuid4

from compiler import decorators

@decorators.service
class UniqueId:
    def __init__(self):
        pass

    def upload_unique_id(self, req_id):
        review_id = str(uuid4())
        promise = AsyncInvoke('ComposeReview', "upload_unique_id", req_id, review_id)
        Wait(promise)
