from algorithms.parameters import params
from .constraintFuncs import *
class Fitness:
    def __init__(self, problemElements):
        #the objectives that make up the objective function
        self.maxDrones = problemElements[0]
        self.maxDistanceTraveled = self.maxDrones * params["dayLength"] * params["droneSpeed"]
        self.maxBatteries = problemElements[1]
    
    def evaluate(self, drones):
        maxScore = 1000
        noObjectives = 3 #the number of objectives listed in the initialiser 
        actualDistanceTraveled = 0
        for drone in drones:
            for trip in drone.trips:
                actualDistanceTraveled += Node.distanceCalc(*[action.node for action in trip.actions])
        
        actualDronesUsed = len(drones)
        actualBatteriesUsed = countBatteriesUsed(drones)
        
        distanceNormalised = actualDistanceTraveled/self.maxDistanceTraveled
        dronesNormalised = actualDronesUsed/self.maxDrones
        batteriesNormalised = actualBatteriesUsed/self.maxBatteries

        normalisedObjectivValues = [distanceNormalised, dronesNormalised, batteriesNormalised]

        return int(sum([obj * (maxScore/noObjectives) for obj in normalisedObjectivValues]))