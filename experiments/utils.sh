#!/bin/bash

function wait_until_pods()
{
    local target=$1

    echo "Waiting for rollout (target: $target)..."
    while [ "$(kubectl get pods --no-headers | wc -l)" -ne $target ]
    do
        echo -n "."
        sleep 2
    done
    echo ""
}
