#!/bin/bash

trap "exit" INT

## Source a shell library with useful components
source utils.sh

scale=2
threads=4
connections=16
duration=60s
sleep_dur=30


function deploy_and_run()
{
    echo "Running with: ${extra_args}" # necessary for the plotting script
    python3 test_services.py "${csv_file}" knative \
        --docker_io_username konstantinoskallas --scale "${scale}" ${extra_args}
    wait_until_pods 6
    echo "Rate: 1"
    ./wrk2/wrk -t1 -c1 -d${duration} -R1 --latency http://${LOAD_BALANCER_IP}/req -s ${wrk_file} #| grep -e "Thread Stats" -e "Latency" -e "^Requests/sec:" -e "Non-2xx or 3xx responses:"
    python3 scripts/clear_db.py

    for rate in $rates
    do
        python3 test_services.py "${csv_file}" knative \
            --docker_io_username konstantinoskallas --scale "${scale}" ${extra_args}
        wait_until_pods 6
        echo "Rate: ${rate}"
        ./wrk2/wrk -t${threads} -c${connections} -d${duration} -R${rate} --latency http://${LOAD_BALANCER_IP}/req -s ${wrk_file} # | grep -e "Thread Stats" -e "Latency" -e "^Requests/sec:" -e "Non-2xx or 3xx responses:"
        kn service delete --all
        python3 scripts/clear_db.py
        wait_until_pods 0
    done
}



function run_tree()
{
    export benchmark="tree"
    ## These are the max rates
    export rates="5 10 15 20 25 30 40 50 60 70 80 90"
    export services="callertxn backend1 backend2"
    export wrk_file="${benchmark}.lua"
    export csv_file="${benchmark}.csv"

    echo "Executing: -t${threads} -c${connections} -d${duration} -s ${wrk_file}"

    ## mu2sls
    export extra_args="--enable_logging --enable_txn --enable_custom_dict"
    export rates="10 15 20 25"
    deploy_and_run
    python3 scripts/clear_db.py

    ## mu2sls (w/o OD)
    export extra_args="--enable_logging --enable_txn"
    export rates=""
    deploy_and_run
    python3 scripts/clear_db.py

    ## unsafe (w/ FT)
    export extra_args="--enable_logging"
    export rates="10 15 20 25 30 40 50 60 70 80 90"
    deploy_and_run
    python3 scripts/clear_db.py
}



python3 scripts/clear_db.py
kn service delete --all
wait_until_pods 0
run_tree
