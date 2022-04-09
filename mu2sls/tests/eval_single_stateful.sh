#!/bin/bash

trap "exit" INT

threads=4
connections=16
duration=30s
file=single-stateful.lua

function run_wrk()
{

    echo "Rate: 1"
        ./wrk2/wrk -t1 -c1 -d${duration} -R1 --latency http://${LOAD_BALANCER_IP}/req -s ${file} #| grep -e "Thread Stats" -e "Latency" -e "^Requests/sec:" -e "Non-2xx or 3xx responses:"

    for rate in 20 40 60 80 100 120 140 160 180 240 300 360 
    do
        ## TODO: Also check for patterns of non 2xx responses
        echo "Rate: ${rate}"
        ./wrk2/wrk -t${threads} -c${connections} -d${duration} -R${rate} --latency http://${LOAD_BALANCER_IP}/req -s ${file} # | grep -e "Thread Stats" -e "Latency" -e "^Requests/sec:" -e "Non-2xx or 3xx responses:"
    done
}

echo "Executing: -t${threads} -c${connections} -d${duration} -s ${file}"


extra_args=""
python3 test_services.py single-stateful.csv knative \
    --docker_io_username konstantinoskallas ${extra_args}
echo "Running with: ${extra_args}"
run_wrk

extra_args="--enable_logging"
python3 test_services.py single-stateful.csv knative \
    --docker_io_username konstantinoskallas ${extra_args}
echo "Running with: ${extra_args}"
run_wrk

extra_args="--enable_txn"
python3 test_services.py single-stateful.csv knative \
    --docker_io_username konstantinoskallas ${extra_args}
echo "Running with: ${extra_args}"
run_wrk

extra_args="--enable_logging --enable_txn"
python3 test_services.py single-stateful.csv knative \
    --docker_io_username konstantinoskallas ${extra_args}
echo "Running with: ${extra_args}"
run_wrk

## TODO: Investigate why Logging with txn is faster than logging without txn (in general why txn is so fast)
##
## TODO: Plot results for better understanding