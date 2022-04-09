#!/bin/bash

threads=4
connections=16
duration=30s
file=single-stateful.lua

echo "Executing: -t${threads} -c${connections} -d${duration} -s ${file}"

echo "Rate: 1"
    ./wrk2/wrk -t1 -c1 -d${duration} -R1 http://${LOAD_BALANCER_IP}/req -s ${file} | grep -e "Thread Stats" -e "Latency" -e "^Requests/sec:"

for rate in 60 100 140 180 220 260 300 340 380 
do
    echo "Rate: ${rate}"
    ./wrk2/wrk -t${threads} -c${connections} -d${duration} -R${rate} http://${LOAD_BALANCER_IP}/req -s ${file} | grep -e "Thread Stats" -e "Latency" -e "^Requests/sec:"
done