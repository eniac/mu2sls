from compiler import decorators

@decorators.service
class MovieInfo(object):
    def __init__(self):
        self.movie_infos = {} # type: Persistent[dict]

    def write_movie_info(self, info):
        self.movie_infos[info['movie_id']] = info

    def read_movie_info(self, movie_id):
        return self.movie_infos[movie_id]

    def upload_rating(self, movie_id, sum_uncommited_rating, num_uncommited_rating):
        info = self.movie_infos[movie_id]
        info['avg_rating'] = (info['avg_rating'] + sum_uncommited_rating) / (info['num_rating'] + num_uncommited_rating)
        info['num_rating'] += num_uncommited_rating
        self.movie_infos[movie_id] = info
