from compiler import decorators

@decorators.service
class Hotel(object):
    def __init__(self):
        self.hotels = {} # type: Persistent[dict]

    async def reserve_hotel(self, hotel_id, user_id):
        ## Retrieve the hotel from the database
        hotel = self.hotels[hotel_id]

        ## If there is capacity add the user in the hotel clients
        if hotel["capacity"] > 0:
            hotel["clients"].append(user_id)
            hotel["capacity"] -= 1
            self.hotels[hotel_id] = hotel
            return True
        else:
            return False

    async def add_hotel(self, hotel_id, capacity):
        self.hotels[hotel_id] = {"hotel_id": hotel_id,
                                 "clients": [],
                                 "capacity": capacity}