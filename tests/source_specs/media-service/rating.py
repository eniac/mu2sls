from compiler import decorators

@decorators.service
class Rating(object):
    def __init__(self):
        pass

    def upload_rating(self, req_id, rating):
        res = SyncInvoke('ComposeReview', "upload_rating", req_id, rating)
        return res

