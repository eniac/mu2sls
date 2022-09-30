#!/bin/bash

function deploy_service()
{
    local docker_io_username=$1
    local service_name=$2
    local docker_io_image_name=$3
    local scale=$4

    echo "Deploying ${service_name} with scale=${scale}..."
    echo "|-- Configuration arguments: ${@:5}"


    ## First check that the kourier system is running
    kubectl --namespace kourier-system get service kourier > /dev/null
    retVal=$?
    if [ $retVal -ne 0 ]; then
        echo "Error: kubectl get service kourier didn't succeed!"
        exit $retval
    fi

    source setup_env_vars.sh

    if [ -z "$LOAD_BALANCER_IP" ]; then
        echo "Error: LOAD_BALANCER_IP is not set!"
        exit 1
    fi

    if [ -z "$FDB_CLUSTER_DATA" ]; then
        echo "Error: FDB_CLUSTER_DATA is not set!"
        exit 1
    fi

    service_exists="$(kn service list | grep ^${service_name}\  )"

    ## The docker.io image name
    image_name="docker.io/${docker_io_username}/${docker_io_image_name}"
    echo "Downloading image from ${image_name}..."

    ## Doesn't exist
    if [ -z "$service_exists" ]; then
        kn service create "${service_name}" --image "${image_name}" \
            --scale-init ${scale} --scale-min ${scale} --scale-max ${scale} --annotation "autoscaling.knative.dev/target=500" \
            --env "LOAD_BALANCER_IP=${LOAD_BALANCER_IP}" \
            --env "FDB_CLUSTER_DATA=${FDB_CLUSTER_DATA}" "${@:5}"
    else
        kn service update "${service_name}" --image "${image_name}" \
            --scale-init ${scale} --scale-min ${scale} --scale-max ${scale} --annotation "autoscaling.knative.dev/target=500" \
            --env "LOAD_BALANCER_IP=${LOAD_BALANCER_IP}" \
            --env "FDB_CLUSTER_DATA=${FDB_CLUSTER_DATA}" "${@:5}"
    fi
}

username=${1?Please provide a docker.io username}
service_name=${2?Please provide the service name as it will appear in knative}
docker_io_image_name=${3?Please provide the docker.io image name}
scale=${4?Please provide the number of nodes per service}

deploy_service "${username}" "${service_name}" "${docker_io_image_name}" "${scale}" "${@:5}"