import json
import os

from scripts.local_dev import *

MU2SLS_TOP = os.getenv('MU2SLS_TOP')
DEPLOYMENT_FILE = f'{MU2SLS_TOP}/tests/media-service-test.csv'

## TODO: Extend it to do the calls using SyncInvoke maybe?
##       Then it would be possible to use it to test non-local deployments too.
def main():
    deployed_services = deploy_from_deployment_file(DEPLOYMENT_FILE)

    # print(deployed_services)

    username = "red_ad"
    password = "1234"

    ## Login with user
    deployed_services['User'].register_user("Red", "Adams", username, password)
    assert list(deployed_services['User'].users.values())[0]['first_name'] == "Red"

    ## Add movie
    deployed_services['MovieId'].register_movie_id("Titanic", '42')
    assert 'Titanic' in deployed_services['MovieId'].movie_ids.keys()

    ## Add plot and movie info
    info = json.loads('{"movie_id": "42", "title": "Titanic", "casts": [], "plot_id": "299534", "thumbnail_ids": ["/or06FN3Dka5tukK1e9sl16pB3iy.jpg"], "photo_ids": [], "video_ids": [], "avg_rating": 8.6, "num_rating": 4789}')
    deployed_services['MovieInfo'].write_movie_info(info)
    assert sorted(list(deployed_services['MovieInfo'].movie_infos.get("42").items())) == sorted(list(info.items()))
    deployed_services['Plot'].write_plot(info['plot_id'], "ship hits iceberg")
    assert deployed_services['Plot'].plots.get("299534") == 'ship hits iceberg'

    ## Compose Review
    deployed_services['Frontend'].compose(username, password, "Titanic", 5, "Titanic is the worst movie I have ever watched!")
    assert len(deployed_services['ComposeReview'].reqs.items()) == 0

    ## TODO: Can use populate.py and compressed.json to populate movies and users
    

if __name__ == '__main__':
    main()
