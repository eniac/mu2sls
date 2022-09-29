## Run the small applications
bash eval_small_applications.sh
sleep 60

## Run the real-world applications
bash eval_media.sh | tee media-service-test.log
sleep 60
bash eval_hotel_reservation.sh | hotel-reservation.log
sleep 60
