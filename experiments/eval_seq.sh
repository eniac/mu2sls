#!/bin/bash

trap "exit" INT

## Source a shell library with useful components
source utils.sh

function deploy_and_run()
{
    local npods=$1
    echo "Running with: ${extra_args}" # necessary for the plotting script
    python3 test_services.py "${csv_file}" knative \
        --docker_io_username konstantinoskallas --scale 1 ${extra_args}
    wait_until_pods "${npods}"
    python3 seq.py --name "${benchmark}"
    python3 scripts/clear_db.py
}

function deploy_and_run_media()
{
    local npods=$1
    echo "Running with: ${extra_args}" # necessary for the plotting script
    python3 test_services.py "${csv_file}" knative \
        --docker_io_username konstantinoskallas --scale 1 ${extra_args}
    wait_until_pods "${npods}"
    python3 populate_media.py > /dev/null 2>&1
    sleep 10
    python3 seq.py --name "${benchmark}"
    python3 scripts/clear_db.py
}

function deploy_and_run_hotel() {
    local npods=$1
    echo "Running with: ${extra_args}" # necessary for the plotting script
    python3 test_services.py "${csv_file}" knative \
        --docker_io_username konstantinoskallas --scale 1 ${extra_args}
    wait_until_pods "${npods}"
    python3 populate_hotel.py > /dev/null 2>&1
    sleep 10
    python3 seq.py --name "${benchmark}"
    python3 scripts/clear_db.py
}

function run_tree()
{
    export benchmark="tree"
    export services="callertxn backend1 backend2"
    export wrk_file="${benchmark}.lua"
    export csv_file="${benchmark}.csv"

    export extra_args="--enable_logging"
    deploy_and_run 3

    export extra_args=""
    deploy_and_run 3

    python3 scripts/clear_db.py
    kn service delete --all
    wait_until_pods 0
}

function run_single_stateful()
{
    export benchmark="single-stateful"
    export services="backend"
    export wrk_file="${benchmark}.lua"
    export csv_file="${benchmark}.csv"

    export extra_args="--enable_logging"
    deploy_and_run 1

    export extra_args=""
    deploy_and_run 1

    python3 scripts/clear_db.py
    kn service delete --all
    wait_until_pods 0
}

function run_chain()
{
    export benchmark="chain"
    export services="caller1 caller2 backend"
    export wrk_file="${benchmark}.lua"
    export csv_file="${benchmark}.csv"

    export extra_args="--enable_logging"
    deploy_and_run 3

    export extra_args=""
    deploy_and_run 3

    python3 scripts/clear_db.py
    kn service delete --all
    wait_until_pods 0
}

function run_media()
{
    export benchmark="media-service-test"
    export services="composereview frontend movieid moviereview reviewstorage text uniqueid user userreview"
    export wrk_file="${benchmark}.lua"
    export csv_file="${benchmark}.csv"

    export extra_args="--enable_logging"
    deploy_and_run_media 9

    export extra_args=""
    deploy_and_run_media 9

    python3 scripts/clear_db.py
    kn service delete --all
    wait_until_pods 0
}

function run_hotel()
{
    export benchmark="hotel-reservation"
    export services="frontend hotel flight order"
    export wrk_file="${benchmark}.lua"
    export csv_file="${benchmark}.csv"

    export extra_args="--enable_logging"
    deploy_and_run_hotel 4

    export extra_args=""
    deploy_and_run_hotel 4

    python3 scripts/clear_db.py
    kn service delete --all
    wait_until_pods 0
}

python3 scripts/clear_db.py
kn service delete --all
wait_until_pods 0

run_single_stateful
run_chain
run_tree
run_media
run_hotel
