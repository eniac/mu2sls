import time
import logging
from compiler import decorators

@decorators.service
class MovieId(object):
    def __init__(self):
        self.movie_ids = {} # type: Persistent[dict]

    async def upload_movie(self, req_id, title, rating):
        start = time.perf_counter_ns()
        # dict does not have has_key in my version of python
        # if not self.movie_ids.has_key(title):
        # TODO: This is innefficient. We would just use a get with a default. 
        if title not in self.movie_ids:
            return None
        movie_id = self.movie_ids[title]
        p1 = AsyncInvoke('ComposeReview', "upload_movie_id", req_id, movie_id)
        p2 = AsyncInvoke('ComposeReview', "upload_rating", req_id, rating)
        await WaitAll(p1, p2)
        end = time.perf_counter_ns()
        duration = (end - start) / 1000000
        logging.error(f'APP MovieId.upload_movie: {duration}')

    def register_movie_id(self, title, movie_id):
        self.movie_ids[title] = movie_id
