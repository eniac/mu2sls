from compiler import decorators

@decorators.service
class Flight(object):
    def __init__(self):
        self.flights = {} # type: Persistent[dict]

    async def reserve_flight(self, flight_id, user_id):
        ## Retrieve the hotel from the database
        flight = self.flights[flight_id]

        ## If there is capacity add the user in the hotel clients
        if flight["capacity"] > 0:
            flight["clients"].append(user_id)
            flight["capacity"] -= 1
            self.flights[flight_id] = flight
            return True
        else:
            return False

    async def add_flight(self, flight_id, capacity):
        self.flights[flight_id] = {"flight_id": flight_id,
                                   "clients": [],
                                   "capacity": capacity}