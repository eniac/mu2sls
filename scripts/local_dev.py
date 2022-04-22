##
## This module contains utility functions to locally load and test services
##

import importlib
import os
import sys

from runtime.local import logger

deployed_services = {}

class CompiledServiceMetadata:
    def __init__(self, class_name, compiled_file):
        self.class_name = class_name
        self.compiled_file = compiled_file

## This function parses a deployment file to service metadata
def parse_service_metadata_from_deploy_file(deploy_file):
    with open(deploy_file) as f:
        deploy_file_data = f.readlines()
    
    service_metadata = []

    for service_data in deploy_file_data:
        class_name, input_file = service_data.rstrip().split(",")

        compiled_file = os.path.basename(input_file)
        service_metadata.append(CompiledServiceMetadata(class_name, compiled_file))

    return service_metadata



def import_compiled(compiled_module_name):
    return importlib.import_module(compiled_module_name)

def init_local_store(name):
    store = logger.LocalLogger()

    ## Note: No need to do that here, since it is done in the service initialization anyway.
    # store.init_env(name)
    return store

def init_local_beldi_store(name):
    print("Error: Local deployment with Beldi is not supported currently")
    assert False
    store = BeldiStore()
    return store

## TODO: What are the inputs
def local_deploy(compiled_services, store_conf="local"):
    
    service_objects = {}
    clients = {}

    for compiled_service in compiled_services:
        ## Import the module that contains the service
        ##
        ## TODO: Might only work if each service is in a different module
        compiled_module_name = compiled_service.compiled_file.split(".")[0]
        module = import_compiled(compiled_module_name)
        
        ## Initialize a separate store for each service
        if store_conf == "local":
            store = init_local_store(compiled_service.class_name)
        elif store_conf == "beldi":
            store = init_local_beldi_store(compiled_service.class_name)
        else:
            print("Error: Unrecognizable store configuration:", store_conf)
            exit(1)

        ## Find the service by name, and initialize it
        service_class = getattr(module, compiled_service.class_name)
        service_object = service_class(store)

        service_objects[compiled_service.class_name] = service_object

        ## Add the service to clients
        clients[compiled_service.class_name] = service_object
    
    ## Connect services together
    for _service_object_name, service_object in service_objects.items():
        service_object.init_clients(clients)

    return service_objects

def deploy_from_deployment_file(deploy_config_file, store_conf="local"):
    service_metadata = parse_service_metadata_from_deploy_file(deploy_config_file)

    services = local_deploy(service_metadata, store_conf)
    return services

def main():
    global deployed_services
    assert(len(sys.argv) in range(2,4))

    ## TODO: Change that to argparse
    deploy_config_file = sys.argv[1]
    if len(sys.argv) == 3:
        store_conf = sys.argv[2]
    else:
        store_conf = "local"

    deployed_services = deploy_from_deployment_file(deploy_config_file, store_conf)

if __name__ == '__main__':
    main()
