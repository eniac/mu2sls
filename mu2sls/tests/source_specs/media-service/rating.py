from compiler import decorators

@decorators.service
class Rating(object):
    def __init__(self):
        pass

    def upload_rating(self, req_id, rating):
        promise = AsyncInvoke('ComposeReview', "upload_rating", req_id, rating)
        ## TODO: In @Haoran's spec, there is no wait after AsyncInvoke, 
        ##       which means that we exit before waiting for it to end 
        ##       I am not sure if we are able to support that
        res = Wait(promise)
        return res

