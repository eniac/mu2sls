import argparse
import json
import os
import sys

from scripts.local_dev import *
from scripts import knative_dev
import runtime.knative.invoke as knative_invoke_lib
import runtime.local.invoke as local_invoke_lib

MU2SLS_TOP = os.getenv('MU2SLS_TOP')
DEPLOYMENT_FILE = f'{MU2SLS_TOP}/tests/cross-service-txn-test.csv'

## TODO: Extend it to do the calls using SyncInvoke maybe?
##       Then it would be possible to use it to test non-local deployments too.
def main(args):
    store_conf = args.mode
    docker_io_username = args.docker_io_username

    ## For local or local-beldi testing, we need to deploy
    if(store_conf in ["local", "beldi"]):
        deployed_services = deploy_from_deployment_file(DEPLOYMENT_FILE, store_conf)
        # print(deployed_services)

        run_test_deployed_services(deployed_services, local_invoke_lib)
        run_local_deployment_tests(deployed_services)
    elif(store_conf == "knative"):
        ## TODO: Do that automatically
        deployment_list = [('frontend', 'frontend'),
                           ('service1', 'service1'),
                           ('service2', 'service2')]
        knative_dev.deploy_services(docker_io_username, deployment_list)


        service_list = ["Frontend", "Service1", "Service2"]
        services = {k: k for k in service_list}
        run_test_deployed_services(services, knative_invoke_lib)
    else:
        print("Unrecognized test conf")
        exit(1)


    
def run_test_deployed_services(deployed_services, invoke_lib):
    val1 = 5
    val2 = 42

    prev1, prev2, prev3 = invoke_lib.SyncInvoke(deployed_services['Frontend'], "compose", val1)

    # print(prev1, prev2, prev3)

    assert prev1 == prev2 == prev3 == 0

    prev1, prev2, prev3 = invoke_lib.SyncInvoke(deployed_services['Frontend'], "compose", val2)
    assert prev1 == prev2 == prev3 == val1


## These tests can only be ran if we have the instances too
def run_local_deployment_tests(deployed_services):
    pass

## TODO: Generalize those!
def parse_arguments():
    parser = argparse.ArgumentParser()
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
