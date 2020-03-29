from algorithms.parameters import params
from evaluator import constraintFuncs
from generatorObjects.node import Node, Depot
from generatorObjects.package import Package
import copy
from inspect import getmembers, isfunction, signature



class Fitness:
    def __init__(self, problemElements):
        #the objectives that make up the objective function
        self.maxDrones = problemElements[0]
        self.maxDistanceTraveled = self.maxDrones * params["dayLength"] * params["droneSpeed"]
        self.maxBatteries = problemElements[1]
        self.maxLateness = self.calcMaxLateness(problemElements)
        self.originalState_batteriesHeld = copy.deepcopy(Depot.batteriesHeld)
        #other variables (not objectives) 
        self.numberOfPackages = problemElements[3]
        self.packages = self.buildPackages(problemElements)

    def calcMaxLateness(self, problemElements):
        maxLateness = 0
        numberOfCustomers = problemElements[2]
        #start at first customer node 
        index = 7 
        for _ in range(100): 
            closeTime = problemElements[index + 3]
            maxLateness += params["dayLength"] - closeTime
            index += 4
        return maxLateness
    
    def buildPackages(self, problemElements): 
        packages = []
        numberOfCustomers = problemElements[2]
        index = 7 + (numberOfCustomers * 4) #index of the first package in problem file 
        for _ in range(self.numberOfPackages): 
            package = Package(problemElements[index])
            index += 1
            package.weight = problemElements[index]
            index += 1
            package.destination = problemElements[index]
            index += 1
            packages.append(package)
        
        return packages

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

    def hardConstraintScore(self,drones): 
        
        originalState_depotBatteries = copy.deepcopy(Depot.batteriesHeld)
        #produces a list of all functions that only take drones as argument
        droneConstraints = [o[1] for o in getmembers(constraintFuncs) if (isfunction(o[1])) and (len(signature(o[1]).parameters) == 2)]
        constraintViolationScore = 0
        #if any of the drone based constraint functions return False then 1000 penalty is applied
        for function in droneConstraints: 
            if not function(copy.deepcopy(drones), detailed = False):
                Depot.batteriesHeld = originalState_depotBatteries
                print(f"function {function} violated")
                constraintViolationScore += 1000

        if not constraintFuncs.countUniquePackagesDelivered(drones, detailed = False, NoOfPackages = self.numberOfPackages):
            print("violated1")
            constraintViolationScore += 1000
        
        if not constraintFuncs.checkCustomerDemandsSatisfied(copy.deepcopy(drones), detailed = False, packages = self.packages):
            print("violated2")
            constraintViolationScore += 1000
        
        if not constraintFuncs.countBatteriesUsed(drones, detailed = False, maxBatteries = self.maxBatteries):
            print("violated3")
            constraintViolationScore += 1000

        return constraintViolationScore

    def evaluate(self, drones):
        Depot.batteriesHeld = self.originalState_batteriesHeld
        maxScore = 1000
        noObjectives = 3 #the number of objectives listed in the initialiser 

        actualDistanceTraveled = self.actualDistanceCalculation(drones)
        actualLateness = self.actualLatenessCalculation(copy.deepcopy(drones)) #pass a copy of the list so that changing the drone variables don't affect the original list
        actualDronesUsed = len(drones)
        actualBatteriesUsed = constraintFuncs.countBatteriesUsed(drones)
        
        distanceNormalised = actualDistanceTraveled/self.maxDistanceTraveled
        latenessNormalised = actualLateness/self.maxLateness
        dronesNormalised = actualDronesUsed/self.maxDrones
        batteriesNormalised = actualBatteriesUsed/self.maxBatteries

        normalisedObjectivValues = [distanceNormalised, dronesNormalised, batteriesNormalised, latenessNormalised]

        hardConstraintContribution = self.hardConstraintScore(drones)

        return (int(sum([obj * (maxScore/noObjectives) for obj in normalisedObjectivValues]))) + hardConstraintContribution