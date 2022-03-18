from uuid import uuid4

from compiler import decorators

@decorators.service
class Frontend(object):
    def __init__(self):
        pass

    async def compose(self, username, password, title, rating, text):
        token = SyncInvoke('User', 'login', username, password)
        assert token is not None
        req_id = str(uuid4())
        SyncInvoke('ComposeReview', "upload_req", req_id)
        # 4 concurrent sync invokes
        ## TODO: @Haoran Do we actually mean concurrent here? If so they need to be Async
        p1 = AsyncInvoke('UniqueId', "upload_unique_id", req_id)
        p2 = AsyncInvoke('User', "upload_user", req_id, username)
        p3 = AsyncInvoke('MovieId', "upload_movie", req_id, title, rating)
        p4 = AsyncInvoke('Text', "upload_text", req_id, text)

        await WaitAll(p1, p2, p3, p4)
