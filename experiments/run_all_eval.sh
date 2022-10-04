#!/bin/bash

export exec_single_stateful=0
export exec_chain=0
export exec_tree=0
export exec_media=0
export exec_hotel=0
export exec_seq=0

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

    if [ "--seq" == "$item" ]; then
        export exec_seq=1
    fi
done


## Run the small applications
bash eval_small_applications.sh

if [ "$exec_tree" -eq 1 ]; then
    echo -e "Executing Cross Service Txn (tree)....\n\n"
    bash eval_tree.sh | tee tree.log
    ## Cleanup services
    sleep 60
    kn service delete --all
    python3 scripts/clear_db.py
    sudo service foundationdb stop
    sleep 20
    sudo service foundationdb start
    echo -e "Execution of Cross Service Txn (tree) was completed!\n\n"
fi


## Run the real-world applications
if [ "$exec_media" -eq 1 ]; then
    echo -e "Executing media....\n\n"
    bash eval_media.sh | tee media-service-test.log
    ## Cleanup services
    sleep 60
    kn service delete --all
    sudo service foundationdb stop
    sleep 20
    sudo service foundationdb start
    echo -e "Execution of media was completed!\n\n"
fi

## Run the real-world applications
if [ "$exec_hotel" -eq 1 ]; then
    echo -e "Executing hotel....\n\n"
    bash eval_hotel_reservation.sh | tee hotel-reservation.log
    ## Cleanup services
    sleep 60
    kn service delete --all
    sudo service foundationdb stop
    sleep 20
    sudo service foundationdb start
    echo -e "Execution of hotel was completed!\n\n"
fi

if [ "$exec_seq" -eq 1 ]; then
    echo -e "Executing sequential experiments....\n\n"
    bash eval_seq.sh | tee seq.log
    ## Cleanup services
    sleep 60
    kn service delete --all
    sudo service foundationdb stop
    sleep 20
    sudo service foundationdb start
    echo -e "Execution of sequential experiments was completed!\n\n"
fi
