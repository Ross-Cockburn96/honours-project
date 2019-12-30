class Drone:

    def __init__(self, trip):
        self.trips = [trip]
    def addTrip(self, trip):
        self.trips.append(trip)

    def __repr__(self):
        return (str(self.trips))
