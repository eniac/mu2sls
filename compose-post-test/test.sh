#!/bin/bash

## This script runs the composition of serverless and the social network microservices all in one script. 
## It is not meant to be a proper testing infrastructure but rather a first attempt at running the experiment end to end.

export PROJECT_TOP="$(git rev-parse --show-toplevel --show-superproject-working-tree)"
export PARENT="$(dirname "$PROJECT_TOP")"

## Find the Deathstar Bench top, which could either be already exported, or by default expected to be a sibling directory
export DSB_TOP="${DSB_TOP:-${PARENT}/DeathStarBench}"

export previous_dir=`pwd`

cd "${PROJECT_TOP}/compose-post-test"

export gateway_port=8090

exit_on_error()
{
    echo "ERROR: $1"
    exit 1
}

echo "Preparing the OpenFaaS platform..."
kubectl rollout status -n openfaas deploy/gateway
port_forward_log="${previous_dir}/port_forward.log"
kubectl port-forward -n openfaas svc/gateway ${gateway_port}:8080 >"${port_forward_log}" 2>&1 & 
export port_forward_pid=$!
echo "Port forwarding pid is: ${port_forward_pid} and log is: $port_forward_log"

## Make sure to kill the port forwarding pid if we die
cleanup() {
    echo "Killing the port-forward process..."
    kill -9 "${port_forward_pid}" >/dev/null 2>&1 
    cd "${previous_dir}"
}

trap 'cleanup' EXIT

## Sleeping for one second to "ensure" that port-forwarding has succeeded
sleep 1

PASSWORD=$(kubectl get secret -n openfaas basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode; echo)
echo -n $PASSWORD | faas-cli login --username admin --password-stdin -g http://127.0.0.1:${gateway_port}

up_log="${previous_dir}/faas_up.log"
echo "Building and deploying the function... (log: $up_log)"
faas-cli up -f compose-post.yml -g http://127.0.0.1:${gateway_port} >"${up_log}" 2>&1 || exit_on_error "FaaS build failed"

echo "Done with serverless preparation"

cd "${DSB_TOP}/socialNetwork/wrk2"

echo "Stopping any previous microservice deployment..."
docker-compose down

build_log="${previous_dir}/microservice_build.log"
echo "Building compose post image... (log: $build_log)"
docker-compose build compose-post-service >"${build_log}" 2>&1 || exit_on_error "Microservice build failed"

m_up_log="${previous_dir}/microservice_up.log"
echo "Starting the microservice deployment... (log: $m_up_log)"
docker-compose up -d >"${m_up_log}" 2>&1 || exit_on_error "Microservice deployment failed"

## Wait to make sure that everything is set up
##
## TODO: Maybe not needed
sleep 5

threads=2
connections=5
duration=2
rate=10
./wrk -D exp -t ${threads} -c ${connections} \
             -d ${duration} -L -s \
             ./scripts/social-network/compose-post.lua http://localhost:8080/wrk2-api/post/compose \
             -R ${rate}

# echo "Stopping the microservice deployment..."
# docker-compose down