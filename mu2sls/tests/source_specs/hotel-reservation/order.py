from uuid import uuid4

from compiler import decorators

@decorators.service
class Order(object):
    def __init__(self):
        self.orders = {} # type: Persistent[dict]

    async def place_order(self, user_id, flight_id, hotel_id):
        ## TODO: For this to be totally correct, we need to log non-deterministic calls
        ##       like uuid4.
        order_id = str(uuid4())
        self.orders[order_id] = { "order_id": order_id, 
                                  "flight_id": flight_id,
                                  "hotel_id": hotel_id, 
                                  "user_id": user_id}
