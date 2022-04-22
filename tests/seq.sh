#!/bin/bash -ex

for i in {1..1000};
do
  req=$(jo req_id=$(uuidgen) args=[${i}])
  curl --json $req -X POST -H "Host: backend.default.example.com" http://${LOAD_BALANCER_IP}/req > /dev/null 2>&1
done
