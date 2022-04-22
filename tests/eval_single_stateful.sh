#!/bin/bash

trap "exit" INT

## Remember to set min-max scale
scale=2

benchmark="single-stateful"
rates="20 60 100 140 180 220 260 300 340 380"
services="backend"

benchmark="chain"
rates="20 30 40 50 60 70 80 90 100 110"
services="caller1 caller2 backend"

benchmark="tree"
rates="10 20 30 40 50 60 70 80 90 100 110"
services="callertxn backend1 backend2"


threads=4
connections=16
duration=30s
wrk_file="${benchmark}.lua"
csv_file="${benchmark}.csv"

function run_wrk()
{

    echo "Rate: 1"
        ./wrk2/wrk -t1 -c1 -d${duration} -R1 --latency http://${LOAD_BALANCER_IP}/req -s ${wrk_file} #| grep -e "Thread Stats" -e "Latency" -e "^Requests/sec:" -e "Non-2xx or 3xx responses:"

    for rate in $rates
    do
        ## TODO: Also check for patterns of non 2xx responses
        echo "Rate: ${rate}"
        ./wrk2/wrk -t${threads} -c${connections} -d${duration} -R${rate} --latency http://${LOAD_BALANCER_IP}/req -s ${wrk_file} # | grep -e "Thread Stats" -e "Latency" -e "^Requests/sec:" -e "Non-2xx or 3xx responses:"
    done
}

function set_min_max_scale()
{
    for service in $services
    do
        kn service update "$service" --scale-min ${scale} --scale-max ${scale} --annotation "autoscaling.knative.dev/target=500"
    done
}

echo "Executing: -t${threads} -c${connections} -d${duration} -s ${wrk_file}"

echo "Setting scale"
set_min_max_scale

extra_args="--enable_logging --enable_txn --enable_custom_dict"
python3 test_services.py "${csv_file}" knative \
    --docker_io_username konstantinoskallas ${extra_args}
echo "Running with: ${extra_args}"
run_wrk

extra_args="--enable_logging --enable_txn"
python3 test_services.py "${csv_file}" knative \
    --docker_io_username konstantinoskallas ${extra_args}
echo "Running with: ${extra_args}"
run_wrk

extra_args="--enable_txn --enable_custom_dict"
python3 test_services.py "${csv_file}" knative \
    --docker_io_username konstantinoskallas ${extra_args}
echo "Running with: ${extra_args}"
run_wrk

extra_args="--enable_logging --enable_custom_dict"
python3 test_services.py "${csv_file}" knative \
    --docker_io_username konstantinoskallas ${extra_args}
echo "Running with: ${extra_args}"
run_wrk

extra_args="--enable_custom_dict"
python3 test_services.py "${csv_file}" knative \
    --docker_io_username konstantinoskallas ${extra_args}
echo "Running with: ${extra_args}"
run_wrk


extra_args=""
python3 test_services.py "${csv_file}" knative \
    --docker_io_username konstantinoskallas ${extra_args}
echo "Running with: ${extra_args}"
run_wrk

extra_args="--enable_logging"
python3 test_services.py "${csv_file}" knative \
    --docker_io_username konstantinoskallas ${extra_args}
echo "Running with: ${extra_args}"
run_wrk

extra_args="--enable_txn"
python3 test_services.py "${csv_file}" knative \
    --docker_io_username konstantinoskallas ${extra_args}
echo "Running with: ${extra_args}"
run_wrk

