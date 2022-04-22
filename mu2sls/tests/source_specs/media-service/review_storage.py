import time
import logging
from compiler import decorators

@decorators.service
class ReviewStorage(object):
    ## No need for Client factory if we have no clients
    def __init__(self):
        ## We need to add a type to each field
        self.reviews = {} # type: Persistent[dict]

    def store_review(self, review):
        start = time.perf_counter_ns()
        self.reviews[review['review_id']] = review
        end = time.perf_counter_ns()
        duration = (end - start) / 1000000
        logging.error(f'APP ReviewStorage.store: {duration}')

    def read_reviews(self, review_ids):
        res = []
        for review_id in review_ids:
            res.append(self.reviews[review_id])
        return res
