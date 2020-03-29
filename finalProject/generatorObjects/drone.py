
import os 
from new_generator.parameters import Parameters 
from generatorObjects.battery import Battery
class Drone:
    #takes either an individual trip or a list of trips as argument 
    def __init__(self, *args):
        self.trips = list(args)
        self.distanceLeft = Parameters.dayLength * Parameters.droneSpeed #this is the maximum distance a drone can travel in a day 
        self.battery = Battery.createNew()
        self.originalBattery = self.battery
        self.time = 0 #used for decoder 

    def reset(self): 
        self.battery = self.originalBattery
        self.battery.reset()
        self.distanceLeft = Parameters.dayLength * Parameters.droneSpeed
    
    def getAllActions(self):
        actions = [action for trip in self.trips for action in trip.actions]
        return actions

    def __repr__(self):
        return (str(self.trips))
