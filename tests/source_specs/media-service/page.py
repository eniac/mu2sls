from compiler import decorators

##
## This service is used to load the page for a specific movie
##

@decorators.service
class Page(object):
    def __init__(self):
        pass

    def read_page(self, movie_id):
        movie_info = SyncInvoke('MovieInfo', "read_movie_info", movie_id)
        cast_ids = [cast["cast_id"] for cast in movie_info["casts"]]
        # 3 concurrent sync invokes
        cast_infos = SyncInvoke('CastInfo', "read_cast_info", cast_ids)
        plot = SyncInvoke('Plot', "read_plot", movie_info["plot_id"])
        reviews = SyncInvoke('MovieReview', "read_movie_reviews", movie_id)
        return {
            "cast_infos": cast_infos,
            "reviews": reviews,
            "movie_info": movie_info,
            "plot": plot
        }
