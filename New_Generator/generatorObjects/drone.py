import parameters 

class Drone:

    #takes either an individual trip or a list of trips as argument 
    def __init__(self, *args):
        self.trips = list(args)
        
    def addTrip(self, trip):
        self.trips.append(trip)

    def getAllActions(self):
        actions = [action for trip in self.trips for action in trip.actions]
        return actions

    def __repr__(self):
        return (str(self.trips))
