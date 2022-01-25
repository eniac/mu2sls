from compiler import decorators

@decorators.service
class UserReview(object):
    ## We need a generic way to get client-names. I know do it with this clientFactory
    def __init__(self, clientFactory):
        self.reviews = {} # type: Persistent[dict]

        ## We then initialize the client using the class name
        self.review_storage_client = clientFactory('ReviewStorage') # type: Client

    ## Currently the compiler does not handle many syntactically sugared ops. We can handle them but it is engineering work.
    ## Therefore we use:
    ## - reviews.get(x) instead of reviews[x]
    ## - for x in self.reviews.keys() instead of for x in self.reviews
    ## - reviews.update([(key, value)]) instead of reviews[key] = value
    def upload_user_review(self, user_id, review_id, timestamp):
        if user_id in self.reviews.keys():
            prev_reviews = self.reviews.get(user_id)
            self.reviews.update([(user_id,
                                  prev_reviews + [{'review_id': review_id, 'timestamp': timestamp}])])
        else:
            self.reviews.update([(user_id, [{'review_id': review_id, 'timestamp': timestamp}])])

    def read_reviews(self, user_id):        
        review_ids = [review['review_id'] for review in self.reviews.get(user_id, [])]
        ## The SyncInvoke locally will be evaluated simply as a method call.
        # res = self.review_storage_client.read_reviews(review_ids)
        # res = SyncInvoke(self.review_storage_client, "read_reviews", review_ids)
        promise = AsyncInvoke(self.review_storage_client, "read_reviews", review_ids)
        res = Wait(promise)
        return res

