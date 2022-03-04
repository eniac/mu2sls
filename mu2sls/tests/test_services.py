import argparse
import json
import os
import sys

from scripts.local_dev import *
from scripts import knative_dev
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

TEST_FUNC_FROM_FILE = {
    'url-shortener-test.csv': run_test_url_shortener
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
        deployment_list = deployment_list_from_deployment_file(deployment_file)
        knative_dev.deploy_services(docker_io_username, deployment_list)


        service_list = ["Frontend", "Service1", "Service2"]
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
        lines = data.split('\n')
    
    deployment_list = []
    for line in lines:
        python_module_name = line.split('/')[-1].split('.')[0]
        name = python_module_name.replace('_', '')
        deployment_list.append((name, python_module_name))

    return deployment_list

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