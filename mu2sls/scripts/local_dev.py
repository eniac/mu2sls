##
## This module contains utility functions to locally load and test services
##

import importlib
import os
import sys

from runtime import store_stub

deployed_services = []

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

def init_local_store():
    return store_stub.Store()

## TODO: What are the inputs
def local_deploy(compiled_services):
    
    service_objects = {}
    clients = {}

    for compiled_service in compiled_services:
        ## Import the module that contains the service
        ##
        ## TODO: Might only work if each service is in a different module
        compiled_module_name = compiled_service.compiled_file.split(".")[0]
        module = import_compiled(compiled_module_name)
        
        ## Initialize a separate store for each service
        store = init_local_store()

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

def deploy_from_deployment_file(deploy_config_file):
    service_metadata = parse_service_metadata_from_deploy_file(deploy_config_file)

    services = local_deploy(service_metadata)
    return services

def main():
    global deployed_services
    assert(len(sys.argv) == 2)

    deploy_config_file = sys.argv[1]

    deployed_services_ret = deploy_from_deployment_file(deploy_config_file)

if __name__ == '__main__':
    main()
