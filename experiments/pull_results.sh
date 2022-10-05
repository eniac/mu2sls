#!/bin/bash

private_key=${1?Private key path is not given}
node_username=${2?Node username is not given}
node_address=${3?Node address is not given}

scp -i ${private_key} ${node_username}@${node_address}:knative/single_stateful.log ./results/single_stateful.log
scp -i ${private_key} ${node_username}@${node_address}:knative/chain.log ./results/chain.log
scp -i ${private_key} ${node_username}@${node_address}:knative/tree.log ./results/tree.log
scp -i ${private_key} ${node_username}@${node_address}:knative/media-service-test.log ./results/media-service-test.log
scp -i ${private_key} ${node_username}@${node_address}:knative/hotel-reservation.log ./results/hotel-reservation.log
scp -i ${private_key} ${node_username}@${node_address}:knative/seq.log ./results/seq.log