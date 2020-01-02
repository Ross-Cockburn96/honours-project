class Drone:

    def __init__(self, trip):
        self.trips = [trip]
    def addTrip(self, trip):
        self.trips.append(trip)

    def getAllDeliveries(self):
        deliveries = [delivery for trip in self.trips for delivery in trip.deliveries ]
        return deliveries

    def __repr__(self):
        return (str(self.trips))
