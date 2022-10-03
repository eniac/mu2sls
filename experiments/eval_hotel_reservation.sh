#!/bin/bash

trap "exit" INT

## Source a shell library with useful components
source utils.sh

benchmark="hotel-reservation"

threads=2
connections=16
duration=60s
scale=2
method="req"
wrk_file="${benchmark}.lua"
csv_file="${benchmark}.csv"
sleep_dur=60


## Only do the scale setting for the ones that are actually used
services="frontend hotel flight order"

function deploy_and_run()
{
    ## Deploy the services with correct scale
    python3 test_services.py "${csv_file}" knative \
        --docker_io_username konstantinoskallas --scale "${scale}" ${extra_args}
    wait_until_pods 8

    echo "Populating database..."
    python3 populate_hotel.py > /dev/null 2>&1

    echo "Rate: 1"
    ./wrk2/wrk -t1 -c1 -d${duration} -R1 --latency http://${LOAD_BALANCER_IP}/${method} -s ${wrk_file}
    kn service delete --all
    python3 scripts/clear_db.py
    wait_until_pods 0

    for rate in $rates
    do
        ## Deploy the services with correct scale
        python3 test_services.py "${csv_file}" knative \
            --docker_io_username konstantinoskallas --scale "${scale}" ${extra_args}
        wait_until_pods 8

        echo "Populating database..."
        python3 populate_hotel.py > /dev/null 2>&1

        echo "Rate: ${rate}"
        ./wrk2/wrk -t${threads} -c${connections} -d${duration} -R${rate} --latency http://${LOAD_BALANCER_IP}/${method} -s ${wrk_file}
        kn service delete --all
        python3 scripts/clear_db.py
        wait_until_pods 0
    done
}


echo "Executing: -t${threads} -c${connections} -d${duration} -s ${wrk_file}"

export extra_args="--enable_logging --enable_txn --enable_custom_dict"
export rates="2 5 10 15 20 25 30 35 40 45 50"
echo "Running with: ${extra_args}" # necessary for the plotting script
deploy_and_run

export extra_args=""
export rates="2 5 10 20 30 40 50 60 70 80 90"
echo "Running with: ${extra_args}" # necessary for the plotting script
deploy_and_run