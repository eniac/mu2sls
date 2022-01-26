from compiler import decorators

@decorators.service
class Rating(object):
    def __init__(self, clientFactory):
        ## We then initialize the client using the class name
        self.compose_review_client = clientFactory('ComposeReview') # type: Client

    def upload_rating(self, req_id, rating):
        promise = AsyncInvoke(self.compose_review_client, "upload_rating", req_id, rating)
        ## TODO: In @Haoran's spec, there is no wait after AsyncInvoke, 
        ##       which means that we exit before waiting for it to end 
        ##       I am not sure if we are able to support that
        res = Wait(promise)
        return res

