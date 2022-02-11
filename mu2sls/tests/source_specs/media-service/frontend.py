from uuid import uuid4

from compiler import decorators

@decorators.service
class Frontend(object):
    def __init__(self):
        pass

    def compose(self, username, password, title, rating, text):
        token = SyncInvoke('User', 'login', username, password)
        assert token is not None
        req_id = str(uuid4())
        SyncInvoke('ComposeReview', "upload_req", req_id)
        # 4 concurrent sync invokes
        ## TODO: @Haoran Do we actually mean concurrent here? If so they need to be Async
        SyncInvoke('UniqueId', "upload_unique_id", req_id)
        SyncInvoke('User', "upload_user", req_id, username)
        SyncInvoke('MovieId', "upload_movie", req_id, title, rating)
        SyncInvoke('Text', "upload_text", req_id, text)
