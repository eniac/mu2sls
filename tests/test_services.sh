#!/bin/bash

##
## This script compiles, deploys, and tests the media service application
##

deployment_file=${1?Deployment file not given}
store_conf=${2:-local}

export MU2SLS_TOP=${MU2SLS_TOP:-$(git rev-parse --show-toplevel --show-superproject-working-tree)/mu2sls}

test_deploy_dir="${MU2SLS_TOP}/tests/target/"

## Compile the services to the target dir
"${MU2SLS_TOP}/scripts/compile_services.sh" "${deployment_file}" "${test_deploy_dir}" 

## Save mu2sls in pythonpath so that we can import
export PYTHONPATH="${PYTHONPATH}:${MU2SLS_TOP}:${test_deploy_dir}"

source "${MU2SLS_TOP}/scripts/source_fdb_env_var.sh"

## Locally deploy
python3 "${MU2SLS_TOP}/tests/test_services.py" "$deployment_file" "$store_conf"