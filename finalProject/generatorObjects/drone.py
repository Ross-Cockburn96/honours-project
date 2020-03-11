
import os 
print (os.getcwd())
import new_generator.parameters as parameters
from generatorObjects.battery import Battery
class Drone:
    #takes either an individual trip or a list of trips as argument 
    def __init__(self, *args):
        self.trips = list(args)
        self.distanceLeft = parameters.dayLength * parameters.droneSpeed #this is the maximum distance a drone can travel in a day 
        self.battery = Battery.createNew()

    def getAllActions(self):
        actions = [action for trip in self.trips for action in trip.actions]
        return actions

    def __repr__(self):
        return (str(self.trips))
