from uuid import uuid4

from compiler import decorators

@decorators.service
class Frontend(object):
    def __init__(self):
        pass

    def compose(self, username, password, title, rating, text):
        token = SyncInvoke('User', 'login', username, password)
        assert token is not None
        req_id = uuid4()
        SyncInvoke('ComposeReview', "upload_req", req_id)
        # 4 concurrent sync invokes
        SyncInvoke('UniqueId', "upload_unique_id", req_id)
        SyncInvoke('User', "upload_user", req_id, username)
        SyncInvoke('MovieId', "upload_movie", title, req_id, rating)
        SyncInvoke('Text', "upload_text", req_id, text)
