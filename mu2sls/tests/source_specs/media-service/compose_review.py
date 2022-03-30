from datetime import datetime

from compiler import decorators

@decorators.service
class ComposeReview(object):
    def __init__(self):
        self.reqs = {} # type: Persistent[dict]
        
    ## Notes:
    ## The reqs field in this service is only acting as a cache, 
    ##   since its importance is simply to delegate the writing to the actual review services.

    async def _try_compose_and_upload(self, req_id):
        review = self.reqs[req_id]
        if review["counter"] == 5:
            p1 = AsyncInvoke('ReviewStorage', "store_review", review)

            ## TODO: What should we do for the non-deterministic time?
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            p2 = AsyncInvoke('UserReview', "upload_user_review", review["user_id"], review["review_id"], ts)
            p3 = AsyncInvoke('MovieReview', "upload_movie_review", review["movie_id"], review["review_id"], ts)
            self.reqs.pop(req_id)

            await WaitAll(p1, p2, p3)

    def upload_req(self, req_id):
        self.reqs[req_id] = {"counter": 0}

    def upload_unique_id(self, req_id, review_id):
        review = self.reqs[req_id]
        review["review_id"] = review_id
        review["counter"] += 1
        self.reqs[req_id] = review
        self._try_compose_and_upload(req_id)

    def upload_text(self, req_id, text):
        review = self.reqs[req_id]
        review["text"] = text
        review["counter"] += 1
        self.reqs[req_id] = review 
        self._try_compose_and_upload(req_id)

    def upload_rating(self, req_id, rating):
        review = self.reqs[req_id]
        review["rating"] = rating
        review["counter"] += 1
        self.reqs[req_id] = review
        self._try_compose_and_upload(req_id)

    def upload_user_id(self, req_id, user_id):
        review = self.reqs[req_id]
        review["user_id"] = user_id
        review["counter"] += 1
        self.reqs[req_id] = review
        self._try_compose_and_upload(req_id)

    def upload_movie_id(self, req_id, movie_id):
        review = self.reqs[req_id]
        review["movie_id"] = movie_id
        review["counter"] += 1
        self.reqs[req_id] = review
        self._try_compose_and_upload(req_id)
