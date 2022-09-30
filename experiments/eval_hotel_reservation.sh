#!/bin/bash

trap "exit" INT

## Source a shell library with useful components
source utils.sh

benchmark="hotel-reservation"

threads=4
connections=16
duration=60s
scale=1
method="req"
wrk_file="${benchmark}.lua"
csv_file="${benchmark}.csv"
sleep_dur=60


# services="composereview castinfo frontend movieid movieinfo moviereview page plot rating reviewstorage text uniqueid user userreview"
## Only do the scale setting for the ones that are actually used
services="frontend hotel flight order"

function run_wrk()
{

    echo "Rate: 1"
    ./wrk2/wrk -t1 -c1 -d${duration} -R1 --latency http://${LOAD_BALANCER_IP}/${method} -s ${wrk_file} #| grep -e "Thread Stats" -e "Latency" -e "^Requests/sec:" -e "Non-2xx or 3xx responses:"
    sleep "${sleep_dur}"

    for rate in $rates
    do
        ## TODO: Also check for patterns of non 2xx responses
        echo "Rate: ${rate}"
        ./wrk2/wrk -t${threads} -c${connections} -d${duration} -R${rate} --latency http://${LOAD_BALANCER_IP}/${method} -s ${wrk_file} # | grep -e "Thread Stats" -e "Latency" -e "^Requests/sec:" -e "Non-2xx or 3xx responses:"
        sleep "${sleep_dur}"
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

## Only needs to be done once
python3 test_services.py "${csv_file}" knative \
    --docker_io_username tauta ${extra_args}
sleep "${sleep_dur}"
set_min_max_scale

export extra_args=""
export rates="2 5 10 15 20 25 30 35 40 45 50"
python3 test_services.py "${csv_file}" knative \
    --docker_io_username tauta ${extra_args}
echo "Populating database..."
python3 populate_hotel.py
echo "Running with: ${extra_args}"
run_wrk

export extra_args="--enable_logging --enable_txn --enable_custom_dict"
export rates="2 5 10 20 30 40 50 60 70 80 90"
python3 test_services.py "${csv_file}" knative \
    --docker_io_username tauta ${extra_args}
echo "Populating database..."
python3 populate_hotel.py
echo "Running with: ${extra_args}"
run_wrk

