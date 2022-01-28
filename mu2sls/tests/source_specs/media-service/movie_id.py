from compiler import decorators

@decorators.service
class MovieId(object):
    def __init__(self):
        self.movie_ids = {} # type: Persistent[dict]

    def upload_movie(self, req_id, title, rating):
        # dict does not have has_key in my version of python
        # if not self.movie_ids.has_key(title):
        # TODO: This is innefficient. We would just use a get with a default. 
        if title not in self.movie_ids.keys():
            return None
        movie_id = self.movie_ids.get(title)
        p1 = AsyncInvoke('ComposeReview', "upload_movie_id", req_id, movie_id)
        p2 = AsyncInvoke('ComposeReview', "upload_rating", req_id, rating)
        WaitAll(p1, p2)

    def register_movie_id(self, title, movie_id):
        self.movie_ids.update([(title, movie_id)])
