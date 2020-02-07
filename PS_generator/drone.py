import parameters 

class Drone:

    #takes either an individual trip or a list of trips as argument 
    def __init__(self, *args):
        self.trips = list(args)
        self.charge = parameters.batteryCharge

    def addTrip(self, trip):
        self.trips.append(trip)

    def getAllDeliveries(self):
        deliveries = [delivery for trip in self.trips for delivery in trip.deliveries ]
        return deliveries

    def __repr__(self):
        return (str(self.trips))
