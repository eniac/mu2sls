#!/bin/bash

docker_io_username=${1?docker.io username not given}

function build()
{
    local service_name=$1
    echo "Building ${service_name}..."
    docker build -f "./${service_name}/Dockerfile" -t "${docker_io_username}/${service_name}" .
}

function push()
{
    local service_name=$1
    echo "Pushing ${service_name}..."
    docker push "${docker_io_username}/${service_name}"
}
