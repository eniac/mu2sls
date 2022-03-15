import argparse
import json
import os
import sys

from scripts.local_dev import *
from scripts import knative_dev
from scripts import clear_db
import runtime.knative.invoke as knative_invoke_lib
import runtime.local.invoke as local_invoke_lib

MU2SLS_TOP = os.getenv('MU2SLS_TOP')

def run_test_url_shortener(deployed_services, invoke_lib):
    service = deployed_services['UrlShortener']

    ret1_found, ret1_short = invoke_lib.SyncInvoke(service, "ShortenUrls", "google.com")
    assert ret1_found == 'NotFound'

    ret2_found, ret2_short = invoke_lib.SyncInvoke(service, "ShortenUrls", "google.com")
    assert ret2_found == 'Found'
    assert ret1_short == ret2_short

    ret3_found, ret3_short = invoke_lib.SyncInvoke(service, "ShortenUrls", "yahoo.com")
    assert ret3_found == 'NotFound'

    ret1, ret2 = invoke_lib.SyncInvoke(service, "ComposeUrls", ["google.com", "yahoo.com"])
    assert ret1 == ret1_short
    assert ret2 == ret3_short

def run_test_media_service(deployed_services, invoke_lib):
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

def run_test_cross_service_txn(deployed_services, invoke_lib):
    val1 = 5
    val2 = 42

    prev1, prev2, prev3 = invoke_lib.SyncInvoke(deployed_services['Frontend'], "compose", val1)

    print("Call 1:", prev1, prev2, prev3)

    assert prev1 == prev2 == prev3 == [val1]

    prev1, prev2, prev3 = invoke_lib.SyncInvoke(deployed_services['Frontend'], "compose", val2)
    print("Call 2:", prev1, prev2, prev3)
    assert prev1 == prev2 == prev3 == [val1, val2]


def run_test_cross_service_txn_abort(deployed_services, invoke_lib):
    val1 = 5
    val2 = 42

    prev = invoke_lib.SyncInvoke(deployed_services['FrontendAbort'], "compose", val1)

    print("Call 1:", prev)

    assert prev == []

    prev = invoke_lib.SyncInvoke(deployed_services['FrontendAbort'], "compose", val2)
    print("Call 2:", prev)
    assert prev ==  []

TEST_FUNC_FROM_FILE = {
    'url-shortener-test.csv': run_test_url_shortener,
    'media-service-test.csv': run_test_media_service,
    'cross-service-txn-test.csv': run_test_cross_service_txn,
    'cross-service-txn-abort-test.csv': run_test_cross_service_txn_abort
}

## TODO: Extend it to do the calls using SyncInvoke maybe?
##       Then it would be possible to use it to test non-local deployments too.
def main(args):
    store_conf = args.mode
    docker_io_username = args.docker_io_username
    deployment_file = args.deployment_file

    ## For local or local-beldi testing, we need to deploy
    if(store_conf in ["local", "beldi"]):
        deployed_services = deploy_from_deployment_file(deployment_file, store_conf)
        # print(deployed_services)

        run_test_deployed_services(deployed_services, deployment_file, local_invoke_lib)
    elif(store_conf == "knative"):
        ## First clean up beldi db
        clear_db.main()

        deployment_list, service_list = deployment_list_from_deployment_file(deployment_file)
        knative_dev.deploy_services(docker_io_username, deployment_list, deployment_file)

        services = {k: k for k in service_list}
        run_test_deployed_services(services, deployment_file, knative_invoke_lib)
    else:
        print("Unrecognized test conf")
        exit(1)

def run_test_deployed_services(deployed_services, deployment_file, invoke_lib):
    deployment_file_basename = deployment_file.split('/')[-1]
    test_func = TEST_FUNC_FROM_FILE[deployment_file_basename]

    return test_func(deployed_services, invoke_lib)

## TODO: Very hacky
def deployment_list_from_deployment_file(deployment_file):
    with open(deployment_file) as f:
        data = f.read()
        lines = data.rstrip().split('\n')
    
    deployment_list = []
    for line in lines:
        python_module_name = line.split('/')[-1].split('.')[0]
        name = python_module_name.replace('_', '')
        deployment_list.append((name, python_module_name))

    service_list = []
    for line in lines:
        service_class_name = line.split(',')[0]
        service_list.append(service_class_name)

    return deployment_list, service_list

## TODO: Generalize those!
def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("deployment_file", 
                        help="the deployment file (a csv)")
    parser.add_argument("mode", 
                        help="the testing mode",
                        choices=["local", "beldi", "knative"],
                        default="local")
    parser.add_argument("--docker_io_username", 
                        help="the docker_io username to push/pull the images",
                        default="default")
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_arguments()
    main(args)