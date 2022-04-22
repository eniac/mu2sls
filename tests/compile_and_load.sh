#!/bin/bash

##
## This script compiles and deploys a set of services in a local environment
##

deployment_file=${1?Compilation file not given}

export MU2SLS_TOP=${MU2SLS_TOP:-$(git rev-parse --show-toplevel --show-superproject-working-tree)/mu2sls}

test_deploy_dir="${MU2SLS_TOP}/tests/target/"

## Compile the services to the target dir
"${MU2SLS_TOP}/scripts/compile_services.sh" "${deployment_file}" "${test_deploy_dir}" 

## Save mu2sls in pythonpath so that we can import
export PYTHONPATH="${PYTHONPATH}:${MU2SLS_TOP}:${test_deploy_dir}"

## Locally deploy
python3 -i "${MU2SLS_TOP}/scripts/local_dev.py" "${deployment_file}"

## TODO: Maybe we need to deploy in a new directory

## TODO: We might need a way to discover services
