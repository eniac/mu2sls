from compiler import decorators

@decorators.service
class MovieReview(object):
    def __init__(self):
        self.reviews = {} # type: Persistent[dict]

    def upload_movie_review(self, movie_id, review_id, timestamp):
        if movie_id in self.reviews:
            prev_reviews = self.reviews[movie_id]
            self.reviews[movie_id] = prev_reviews + [{'review_id': review_id, 'timestamp': timestamp}]
        else:
            self.reviews[movie_id] = [{'review_id': review_id, 'timestamp': timestamp}]

    def read_reviews(self, movie_id):
        review_ids = [review['review_id'] for review in self.reviews.get(movie_id, [])]
        res = SyncInvoke('ReviewStorage', "read_reviews", review_ids)
        return res

