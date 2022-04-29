#!/bin/bash

##
## This script compiles a set of services described in a deployment csv file
##

deployment_file=${1?Deployment file not given}
test_deploy_dir=${2?Target directory not given}
## The rest of the arguments are tranfered directly to mu2sls

export MU2SLS_TOP=${MU2SLS_TOP:-$(git rev-parse --show-toplevel --show-superproject-working-tree)}


mkdir -p "${test_deploy_dir}"
echo "Compiled files dir: ${test_deploy_dir}"

while IFS=, read -r class_name input_file
do
    echo "Compiling ${input_file}..."
    output_file_name="$(basename ${input_file})"
    python3 "${MU2SLS_TOP}/mu2sls" "${MU2SLS_TOP}/${input_file}" "${test_deploy_dir}/${output_file_name}" "${@:3}"
done < "${deployment_file}"
