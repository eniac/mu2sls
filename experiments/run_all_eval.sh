#!/bin/bash

export exec_single_stateful=0
export exec_chain=0
export exec_tree=0
export exec_media=0
export exec_hotel=0

for item in "$@"
do
    if [ "--single_stateful" == "$item" ]; then
        export exec_single_stateful=1
    fi
    
    if [ "--chain" == "$item" ]; then
        export exec_chain=1
    fi

    if [ "--tree" == "$item" ]; then
        export exec_tree=1
    fi

    if [ "--media" == "$item" ]; then
        export exec_media=1
    fi

    if [ "--hotel" == "$item" ]; then
        export exec_hotel=1
    fi
done

## Run the small applications
bash eval_small_applications.sh
sleep 60

## Run the real-world applications
if [ "$exec_media" -eq 1 ]; then
    echo -e "Executing media....\n\n"
    bash eval_media.sh | tee media-service-test.log
    ## Cleanup services
    kn service delete --all
    sudo service foundationdb stop
    sleep 60
    sudo service foundationdb start
    echo -e "Execution of media was completed!\n\n"
fi

## Run the real-world applications
if [ "$exec_hotel" -eq 1 ]; then
    echo -e "Executing hotel....\n\n"
    bash eval_hotel_reservation.sh | hotel-reservation.log
    ## Cleanup services
    kn service delete --all
    sudo service foundationdb stop
    sleep 60
    sudo service foundationdb start
    echo -e "Execution of hotel was completed!\n\n"
fi
