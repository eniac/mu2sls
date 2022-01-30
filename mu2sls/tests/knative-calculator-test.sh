#!/bin/bash

##
## This script compiles, deploys (on flask but locally), and tests the calculator service
##

export MU2SLS_TOP=${MU2SLS_TOP:-$(git rev-parse --show-toplevel --show-superproject-working-tree)/mu2sls}

source_file="${MU2SLS_TOP}/tests/source_specs/calculator.py"
test_deploy_dir="${MU2SLS_TOP}/tests/target/"
target_file="${test_deploy_dir}/calculator.py"

mkdir -p "${test_deploy_dir}"

## Compile the service to the target dir
python3 "${MU2SLS_TOP}/mu2sls" -s knative "${source_file}" "${target_file}"

## Save mu2sls in pythonpath so that we can import
export PYTHONPATH="${PYTHONPATH}:${MU2SLS_TOP}:${test_deploy_dir}"

## Deploy flask app
test_log_dir="${MU2SLS_TOP}/tests/logs/"
mkdir -p "${test_log_dir}"
test_log="${test_log_dir}/flask-app-calculator.log"
echo "Deploying calculator as flask app... logs in \"${test_log}\""
python3 "${target_file}" > "${test_log}" 2>&1 &
flask_app_pid=$!

cleanup()
{
    kill -SIGTERM "${flask_app_pid}"
    wait
}

trap cleanup EXIT

echo "Sleeping for 10s to ensure that flask app is running"
sleep 10

execute_cmd_expected()
{
    local cmd=$1
    local expected=$2
    echo "Executing cmd: $cmd"
    local output_file=/tmp/test.out
    $cmd >"${output_file}"
    res=$(cat ${output_file})
    if [ "$res" != "$expected" ]; then
        echo "Response $res not equal to expected: $expected"
        exit 1
    fi
}

execute_cmd_expected "curl -s -X POST localhost:8080/get" '"0"'
execute_cmd_expected "curl -s -X POST localhost:8080/add?number=1" 'null'
execute_cmd_expected "curl -s -X POST localhost:8080/get" '"1"'
execute_cmd_expected "curl -s -X POST localhost:8080/add?number=5" 'null'
execute_cmd_expected "curl -s -X POST localhost:8080/get" '"6"'
