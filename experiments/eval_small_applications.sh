#!/bin/bash

trap "exit" INT

## Source a shell library with useful components
source utils.sh

scale=2
threads=4
connections=16
duration=60s
sleep_dur=30


function run_wrk()
{

    echo "Rate: 1"
    ./wrk2/wrk -t1 -c1 -d${duration} -R1 --latency http://${LOAD_BALANCER_IP}/req -s ${wrk_file} #| grep -e "Thread Stats" -e "Latency" -e "^Requests/sec:" -e "Non-2xx or 3xx responses:"
    python3 scripts/clear_db.py
    sleep "${sleep_dur}"

    for rate in $rates
    do
        echo "Rate: ${rate}"
        ./wrk2/wrk -t${threads} -c${connections} -d${duration} -R${rate} --latency http://${LOAD_BALANCER_IP}/req -s ${wrk_file} # | grep -e "Thread Stats" -e "Latency" -e "^Requests/sec:" -e "Non-2xx or 3xx responses:"
        python3 scripts/clear_db.py
	    sleep "${sleep_dur}"
    done
}


function deploy_and_run()
{
    python3 test_services.py "${csv_file}" knative \
        --docker_io_username konstantinoskallas --scale "${scale}" ${extra_args}
    sleep 30
    echo "Running with: ${extra_args}" # necessary for the plotting script
    run_wrk
    kn service delete --all
    python3 scripts/clear_db.py
    wait_until_pods 0
}

function run_single_stateful()
{

    export benchmark="single-stateful"
    ## These are the max rates
    export rates="20 60 100 140 180 220 260 300 340 380"
    export services="backend"
    export wrk_file="${benchmark}.lua"
    export csv_file="${benchmark}.csv"

    echo "Executing: -t${threads} -c${connections} -d${duration} -s ${wrk_file}"

    echo "Deploying for the first time and running tests (if they exist)..."
    python3 test_services.py "${csv_file}" knative \
        --docker_io_username konstantinoskallas --scale "${scale}" ${extra_args}
    sleep 15

    echo "Setting scale"
    # set_min_max_scale
    sleep 10

    ## mu2sls
    export extra_args="--enable_logging --enable_txn --enable_custom_dict"
    export rates="20 60 100 140 180 220 260 300"
    deploy_and_run

    ## mu2sls (no FT)
    export extra_args="--enable_txn --enable_custom_dict"
    export rates="20 60 100 140 180 220 260 300 340"
    deploy_and_run

    ## mu2sls (w/o OD)
    export extra_args="--enable_logging --enable_txn"
    export rates="20 60 100"
    deploy_and_run

    ## unsage (w/ FT)
    export extra_args="--enable_logging"
    export rates="20 60 100 140 180"
    deploy_and_run

}

function run_chain()
{
    export benchmark="chain"
    ## These are the max rates
    export rates="10 20 30 40 50 60 70 80 90 100 110 120"
    export services="caller1 caller2 backend"
    export wrk_file="${benchmark}.lua"
    export csv_file="${benchmark}.csv"

    echo "Executing: -t${threads} -c${connections} -d${duration} -s ${wrk_file}"

    echo "Deploying for the first time and running tests (if they exist)..."
    python3 test_services.py "${csv_file}" knative \
        --docker_io_username konstantinoskallas --scale "${scale}" ${extra_args}
    sleep 15

    echo "Setting scale"
    # set_min_max_scale
    sleep 10

    ## mu2sls
    export extra_args="--enable_logging --enable_txn --enable_custom_dict"
    export rates="10 20 30 40 50 60 70 80 90 100 110 120"
    deploy_and_run

    ## mu2sls (no FT)
    export extra_args="--enable_txn --enable_custom_dict"
    export rates="10 20 30 40 50 60 70 80 90 100 110 120"
    deploy_and_run

    ## mu2sls (w/o OD)
    export extra_args="--enable_logging --enable_txn"
    export rates="10 20 30 40 50 60 70"
    deploy_and_run

    ## unsage (w/ FT)
    export extra_args="--enable_logging"
    export rates="10 20 30 40 50 60 70 80 90 100 110"
    deploy_and_run

}


if [ "$exec_single_stateful" -eq 1 ]; then
    echo -e "Executing single_stateful....\n\n"
    run_single_stateful | tee single_stateful.log

    ## Cleanup services and DB
    sleep 60
    kn service delete --all
    sudo service foundationdb stop
    sleep 20
    sudo service foundationdb start
    echo -e "Execution of single_stateful was completed!\n\n"
fi

if [ "$exec_chain" -eq 1 ]; then
    echo -e "Executing chain....\n\n"
    run_chain | tee chain.log

    ## Cleanup services
    sleep 60
    kn service delete --all
    sudo service foundationdb stop
    sleep 20
    sudo service foundationdb start
    echo -e "Execution of chain was completed!\n\n"
fi
