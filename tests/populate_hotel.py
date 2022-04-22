import runtime.knative.invoke as knative_invoke_lib
from scripts import clear_db
from scripts import knative_dev

import test_services

CAPACITY = 1e7


def populate(invoke_lib, deployed_services):
    for i in range(100):
        print(i)
        invoke_lib.SyncInvoke(deployed_services['Hotel'], "add_hotel", str(i), CAPACITY, internal=False)
        invoke_lib.SyncInvoke(deployed_services['Flight'], "add_flight", str(i), CAPACITY, internal=False)


def main():
    deployment_file = "hotel-reservation.csv"
    docker_io_username = "tauta"
    clear_db.main()
    deployment_list, service_list = test_services.deployment_list_from_deployment_file(deployment_file)

    # knative_dev.deploy_services(docker_io_username, deployment_list, deployment_file)
    services = {k: k for k in service_list}
    populate(knative_invoke_lib, services)


if __name__ == "__main__":
    main()
