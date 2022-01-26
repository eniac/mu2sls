from compiler import decorators

@decorators.service
class MovieReview(object):
    def __init__(self, clientFactory):
        self.reviews = {} # type: Persistent[dict]

        ## We then initialize the client using the class name
        self.review_storage_client = clientFactory('ReviewStorage') # type: Client

    def read_reviews(self, user_id):        
        review_ids = [review['review_id'] for review in self.reviews.get(user_id, [])]
        ## The SyncInvoke locally will be evaluated simply as a method call.
        # res = self.review_storage_client.read_reviews(review_ids)
        # res = SyncInvoke(self.review_storage_client, "read_reviews", review_ids)
        promise = AsyncInvoke(self.review_storage_client, "read_reviews", review_ids)
        res = Wait(promise)
        return res


    def upload_movie_review(self, movie_id, review_id, timestamp):
        if movie_id in self.reviews.keys():
            prev_reviews = self.reviews.get(movie_id)
            self.reviews.update([(movie_id,
                                  prev_reviews + [{'review_id': review_id, 'timestamp': timestamp}])])
        else:
            self.reviews.update([(movie_id, [{'review_id': review_id, 'timestamp': timestamp}])])

    def read_reviews(self, movie_id):
        review_ids = [review['review_id'] for review in self.reviews.get(movie_id, [])]
        res = SyncInvoke(self.review_storage_client, "read_reviews", review_ids)
        return res

