import json

import test_services

from scripts import clear_db
from scripts import knative_dev

import runtime.knative.invoke as knative_invoke_lib


def populate(invoke_lib, deployed_services, input_file):
    # with open(input_file) as f:
    #     # raw = f.read()
    #     json_data = json.load(f)


    ## Populate movies
    ## No need to populate movies at all
    # i = 0
    # for json_entry in json_data:
    #     movie_id = json_entry['MovieId']
    #     movie_title = json_entry['Title']
    #     movie_plot = "plot"
    #     movie_plot_id = json_entry['PlotId']
        
    #     invoke_lib.SyncInvoke(deployed_services['MovieId'], 
    #                           "register_movie_id", 
    #                           movie_title, movie_id)
        
    #     info = {
    #         'movie_id': movie_id,
    #         'title': movie_title,
    #         'avg_rating': json_entry['AvgRating'],
    #         'num_rating': json_entry['NumRating'],
    #         'plot': movie_plot,
    #         'plot_id': movie_plot_id
    #     }
    #     print(info)
    #     print("number:", i)
    #     i += 1
    #     if i > 100:
    #         break
    #     invoke_lib.SyncInvoke(deployed_services['MovieInfo'], 
    #                       "write_movie_info", 
    #                       info)
        
    #     invoke_lib.SyncInvoke(deployed_services['Plot'],
    #                           "write_plot",
    #                           movie_plot_id, movie_plot)

    ## Populate users
    for i in range(100):
        print(i)
        username = f'username_{i}'
        password = f'password_{i}'
        firstname = f'firstname_{i}'
        lastname = f'lastname_{i}'
        invoke_lib.SyncInvoke(deployed_services['User'], "register_user", 
                              firstname, lastname, username, password)

## TODO: Unharcode them
deployment_file = "media-service-test.csv"
docker_io_username = "konstantinoskallas"

## This is not actually used.
input_file = "compressed.json"

clear_db.main()
## Get a service list from the csv
deployment_list, service_list = test_services.deployment_list_from_deployment_file(deployment_file)

## Deploy the services (uncomment if this was done already)
# knative_dev.deploy_services(docker_io_username, deployment_list, deployment_file)

services = {k: k for k in service_list}

## Populate the service by calling specific services.
populate(knative_invoke_lib, services, input_file)
