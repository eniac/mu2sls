from compiler import decorators

@decorators.service
class ReviewStorage(object):
    ## No need for Client factory if we have no clients
    def __init__(self):
        ## We need to add a type to each field
        self.reviews = {} # type: Persistent[dict]

    def store_review(self, review):
        self.reviews[review['review_id']] = review

    def read_reviews(self, review_ids):
        res = []
        for review_id in review_ids:
            res.append(self.reviews[review_id])
        return res
