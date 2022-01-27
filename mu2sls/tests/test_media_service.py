import os

from scripts.local_dev import *

MU2SLS_TOP = os.getenv('MU2SLS_TOP')
DEPLOYMENT_FILE = f'{MU2SLS_TOP}/tests/media-service-test.csv'

def main():
    deployed_services = deploy_from_deployment_file(DEPLOYMENT_FILE)

    print(deployed_services)

    ## TODO: Add proper tests!

if __name__ == '__main__':
    main()
