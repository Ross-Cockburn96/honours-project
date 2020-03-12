
import os 
print (os.getcwd())
from new_generator.parameters import Parameters 
from generatorObjects.battery import Battery
class Drone:
    #takes either an individual trip or a list of trips as argument 
    def __init__(self, *args):
        self.trips = list(args)
        self.distanceLeft = Parameters.dayLength * Parameters.droneSpeed #this is the maximum distance a drone can travel in a day 
        self.battery = Battery.createNew()

    def getAllActions(self):
        actions = [action for trip in self.trips for action in trip.actions]
        return actions

    def __repr__(self):
        return (str(self.trips))
