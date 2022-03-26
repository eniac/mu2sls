from compiler import decorators

@decorators.service
class UserReview(object):
    def __init__(self):
        self.reviews = {} # type: Persistent[dict]

    ## Currently the compiler does not handle many syntactically sugared ops. We can handle them but it is engineering work.
    ## Therefore we use:
    ## - reviews.get(x) instead of reviews[x]
    ## - for x in self.reviews.keys() instead of for x in self.reviews
    ## - reviews.update([(key, value)]) instead of reviews[key] = value
    def upload_user_review(self, user_id, review_id, timestamp):
        if user_id in self.reviews:
            prev_reviews = self.reviews[user_id]
            self.reviews[user_id] = prev_reviews + [{'review_id': review_id, 'timestamp': timestamp}]
        else:
            self.reviews[user_id] = [{'review_id': review_id, 'timestamp': timestamp}]

    async def read_reviews(self, user_id):        
        review_ids = [review['review_id'] for review in self.reviews.get(user_id, [])]
        ## The SyncInvoke locally will be evaluated simply as a method call.
        # res = self.review_storage_client.read_reviews(review_ids)
        # res = SyncInvoke('ReviewStorage', "read_reviews", review_ids)
        promise = AsyncInvoke('ReviewStorage', "read_reviews", review_ids)
        res = await Wait(promise)
        return res

