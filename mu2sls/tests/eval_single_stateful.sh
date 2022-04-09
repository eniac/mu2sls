#!/bin/bash

threads=4
connections=16
duration=30s
file=single-stateful.lua

python3 test_services.py single-stateful.csv knative \
    --docker_io_username konstantinoskallas \
    --enable_logging

echo "Executing: -t${threads} -c${connections} -d${duration} -s ${file}"

echo "Rate: 1"
    ./wrk2/wrk -t1 -c1 -d${duration} -R1 http://${LOAD_BALANCER_IP}/req -s ${file} | grep -e "Thread Stats" -e "Latency" -e "^Requests/sec:" -e "Non-2xx or 3xx responses:"

for rate in 60 100 140 180 220 260 300 340 380 
do
    ## TODO: Also check for patterns of non 2xx responses
    echo "Rate: ${rate}"
    ./wrk2/wrk -t${threads} -c${connections} -d${duration} -R${rate} http://${LOAD_BALANCER_IP}/req -s ${file} | grep -e "Thread Stats" -e "Latency" -e "^Requests/sec:" -e "Non-2xx or 3xx responses:"
done

## TODO: Investigate why Logging with txn is faster than logging without txn (in general why txn is so fast)
##
## TODO: Plot results for better understanding