#!/bin/bash

##
## This script compiles and deployes a single service in a local environment
##

deployment_file=${1?Compilation file not given}

export MU2SLS_TOP=${MU2SLS_TOP:-$(git rev-parse --show-toplevel --show-superproject-working-tree)/mu2sls}

test_deploy_dir="${MU2SLS_TOP}/tests/target/"

mkdir -p "${test_deploy_dir}"
echo "Compiled files dir: ${test_deploy_dir}"

while IFS=, read -r class_name input_file
do
    echo "Compiling ${input_file}..."
    output_file_name="$(basename ${input_file})"
    python3 "${MU2SLS_TOP}/mu2sls" "${MU2SLS_TOP}/${input_file}" "${test_deploy_dir}/${output_file_name}"
done < "${deployment_file}"

# python3 -i -c "from scripts import local_dev; module = local_dev.import_compiled(\"${output_name}\"); store = local_dev.init_local_store()"

## Save mu2sls in pythonpath so that we can import
export PYTHONPATH="${PYTHONPATH}:${MU2SLS_TOP}:${test_deploy_dir}"

python3 -i "${MU2SLS_TOP}/scripts/local_dev.py" "${deployment_file}"

## TODO: Maybe we need to deploy in a new directory

## TODO: We need a way to load more than one service, and connect the services together
## TODO: We might need a way to discover services

## TODO: Make sure that compilation also adds a method in services that prints info