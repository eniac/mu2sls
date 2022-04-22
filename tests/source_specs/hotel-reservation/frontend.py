from compiler import decorators

from runtime.transaction_exception import TransactionException

@decorators.service
class Frontend(object):
    def __init__(self):
        pass

    async def req(self, user_id, flight_id, hotel_id):
        i = 0
        retry = True
        while retry:
            # print("Trying to perform transaction:", i)
            i += 1
            try:
                ## Begin a transaction
                BeginTx()
                
                ## Try to reserve a hotel
                hotel_fut = AsyncInvoke('Hotel', 'reserve_hotel', hotel_id, user_id)
                
                ## Try to reserve a flight
                flight_fut = AsyncInvoke('Flight', 'reserve_flight', flight_id, user_id)

                hotel_ret, flight_ret = await WaitAll(hotel_fut, flight_fut)
                retry = False
            except TransactionException as e:
                ## This catches transaction failures (and not aborts)
                retry = True

        ## If the hotel reservation failed, abort the transaction and exit
        if not hotel_ret:
            AbortTxNoExc()
            return (hotel_ret, "Hotel Reservation Failed")
        
        ## If the hotel reservation failed, abort the transaction and exit
        if not flight_ret:
            AbortTxNoExc()
            return (flight_ret, "Flight Reservation Failed")
        
        ## Commit the transaction if both succeeded
        CommitTx()

        ## Place the order
        SyncInvoke('Order', 'place_order', user_id, flight_id, hotel_id)
        
        return (True, "Order Successful")

