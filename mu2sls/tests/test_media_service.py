import json
import os

from scripts.local_dev import *
import runtime.knative.invoke as knative_invoke_lib
import runtime.local.invoke as local_invoke_lib

MU2SLS_TOP = os.getenv('MU2SLS_TOP')
DEPLOYMENT_FILE = f'{MU2SLS_TOP}/tests/media-service-test.csv'

## TODO: Extend it to do the calls using SyncInvoke maybe?
##       Then it would be possible to use it to test non-local deployments too.
def main(store_conf="local"):
    deployed_services = deploy_from_deployment_file(DEPLOYMENT_FILE, store_conf)

    # print(deployed_services)

    run_test_deployed_services(deployed_services, local_invoke_lib)
    run_local_deployment_tests(deployed_services)
    
def run_test_deployed_services(deployed_services, invoke_lib):
    username = "red_ad"
    password = "1234"

    ## Login with user
    invoke_lib.SyncInvoke(deployed_services['User'], "register_user", "Red", "Adams", username, password)

    ## Add movie
    invoke_lib.SyncInvoke(deployed_services['MovieId'], 
                          "register_movie_id", 
                          "Titanic", '42')

    ## Add plot and movie info
    info = json.loads('{"movie_id": "42", "title": "Titanic", "casts": [], "plot_id": "299534", "thumbnail_ids": ["/or06FN3Dka5tukK1e9sl16pB3iy.jpg"], "photo_ids": [], "video_ids": [], "avg_rating": 8.6, "num_rating": 4789}')    
    invoke_lib.SyncInvoke(deployed_services['MovieInfo'], 
                          "write_movie_info", 
                          info)

    invoke_lib.SyncInvoke(deployed_services['Plot'],
                          "write_plot",
                          info['plot_id'], "ship hits iceberg")

    ret = invoke_lib.SyncInvoke(deployed_services['Plot'],
                                "read_plot",
                                info['plot_id'])
    assert ret == 'ship hits iceberg'

    ## Compose Review
    invoke_lib.SyncInvoke(deployed_services['Frontend'],
                          "compose",
                          username, password, "Titanic", 5, "Titanic is the worst movie I have ever watched!")

    ## TODO: Can use populate.py and compressed.json to populate movies and users

## These tests can only be ran if we have the instances too
def run_local_deployment_tests(deployed_services):
    assert list(deployed_services['User'].users.values())[0]['first_name'] == "Red"

    assert 'Titanic' in deployed_services['MovieId'].movie_ids.keys()

    info = json.loads('{"movie_id": "42", "title": "Titanic", "casts": [], "plot_id": "299534", "thumbnail_ids": ["/or06FN3Dka5tukK1e9sl16pB3iy.jpg"], "photo_ids": [], "video_ids": [], "avg_rating": 8.6, "num_rating": 4789}')    

    assert sorted(list(deployed_services['MovieInfo'].movie_infos.get("42").items())) == sorted(list(info.items()))

    assert deployed_services['Plot'].plots.get("299534") == 'ship hits iceberg'

    assert len(deployed_services['ComposeReview'].reqs.items()) == 0


if __name__ == '__main__':
    assert(len(sys.argv) in range(1,3))

    ## TODO: Change that to argparse
    if len(sys.argv) == 2:
        store_conf = sys.argv[1]
    else:
        store_conf = "local"
    main(store_conf)
