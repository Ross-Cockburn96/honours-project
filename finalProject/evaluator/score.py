from algorithms.parameters import params
from .constraintFuncs import *
import copy
class Fitness:
    def __init__(self, problemElements):
        #the objectives that make up the objective function
        self.maxDrones = problemElements[0]
        self.maxDistanceTraveled = self.maxDrones * params["dayLength"] * params["droneSpeed"]
        self.maxBatteries = problemElements[1]
        self.maxLateness = self.calcMaxLateness(problemElements)
    
    def calcMaxLateness(self, problemElements):
        maxLateness = 0
        numberOfCustomers = problemElements[2]
        #start at first customer node 
        index = 7 + problemElements[7] + 1
        for _ in range(100): 
            closeTime = problemElements[index + 3]
            maxLateness += params["dayLength"] - closeTime
            index += 4
        return maxLateness

    def actualDistanceCalculation(self, drones):
        actualDistanceTraveled = 0
        for drone in drones:
            for trip in drone.trips:
                actualDistanceTraveled += Node.distanceCalc(*[action.node for action in trip.actions])
        return actualDistanceTraveled
    
    def actualLatenessCalculation(self, drones):
        lateness = 0
        lateCounter = 0 
        regCounter = 0 
        for drone in drones:
            for trip in drone.trips:
                for action in trip.actions[:-1]:
                    if "Delivery" in str(type(action)):
                        openTime = action.node.openTime
                        closeTime = action.node.closeTime
                        if int(drone.time) not in range(openTime, closeTime+1):
                            #if drone is early then add wait time to drone
                            if drone.time < openTime:
                                drone.time += openTime - drone.time
                            #if drone is late 
                            else:
                                lateness += drone.time - closeTime
                    drone.time += int(Node.distanceFinder(action.node, action.nextAction.node) // params["droneSpeed"])
        return int(lateness)      

    def evaluate(self, drones):
        maxScore = 1000
        noObjectives = 3 #the number of objectives listed in the initialiser 

        actualDistanceTraveled = self.actualDistanceCalculation(drones)
        actualLateness = self.actualLatenessCalculation(copy.deepcopy(drones)) #pass a copy of the list so that changing the drone variables don't affect the original list
        actualDronesUsed = len(drones)
        actualBatteriesUsed = countBatteriesUsed(drones)
        
        distanceNormalised = actualDistanceTraveled/self.maxDistanceTraveled
        latenessNormalised = actualLateness/self.maxLateness
        dronesNormalised = actualDronesUsed/self.maxDrones
        batteriesNormalised = actualBatteriesUsed/self.maxBatteries

        normalisedObjectivValues = [distanceNormalised, dronesNormalised, batteriesNormalised, latenessNormalised]

        return int(sum([obj * (maxScore/noObjectives) for obj in normalisedObjectivValues]))