from algorithms.parameters import params
from evaluator import constraintFuncs
from generatorObjects.node import Node, Depot
from generatorObjects.package import Package
from fileParsers.nodeBuilder import buildNodes
from fileParsers.objectBuilder import buildObjects
import copy
from inspect import getmembers, isfunction, signature



class Fitness:
    def __init__(self, problemElements):
   
        self.maxDrones = problemElements[0]
        self.maxBatteries = problemElements[1]
        self.originalState_batteriesHeld = copy.deepcopy(Depot.batteriesHeld)
        
 
        self.numberOfCustomers = problemElements[2]
        self.numberOfPackages = problemElements[3]
        self.numberOfRechargingStations = problemElements[4]
        self.nodes, self.packages = buildNodes(problemElements)

    
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
        maxLateness = 0
        lateCounter = 0 
        regCounter = 0 
        for drone in drones:
            for trip in drone.trips:
                for action in trip.actions[:-1]:
                    if "Delivery" in str(type(action)):
                        openTime = action.node.openTime
                        closeTime = action.node.closeTime
                        maxLateness += params["dayLength"] - closeTime
                        if int(drone.time) not in range(openTime, closeTime+1):
                            #if drone is early then add wait time to drone
                            if drone.time < openTime:
                                drone.time += openTime - drone.time
                            #if drone is late 
                            else:
                                lateness += drone.time - closeTime
                    drone.time += int(Node.distanceFinder(action.node, action.nextAction.node) // params["droneSpeed"])
        return int(lateness), maxLateness      

    def hardConstraintScore(self,drones): 
        print("checking hard constraints")
        originalState_depotBatteries = copy.deepcopy(Depot.batteriesHeld)
        #produces a list of all functions that only take drones as argument
        droneConstraints = [o[1] for o in getmembers(constraintFuncs) if (isfunction(o[1])) and (len(signature(o[1]).parameters) == 2)]
        constraintViolationScore = 0

        #count unique packages 
        packagesScheduled = constraintFuncs.countUniquePackagesDelivered(drones)
        packagesNotScheduled = self.numberOfPackages - packagesScheduled
        packagesNotScheduled_Normalised = packagesNotScheduled/self.numberOfPackages
        scoreContribution_PS = int(packagesNotScheduled_Normalised * 100)
        constraintViolationScore += scoreContribution_PS

        #check customers are given correct packages
        correctlyDeliveredPkgs = constraintFuncs.checkCustomerDemandsSatisfied(copy.deepcopy(drones), self.packages) 
        packagesNotDeliveredCorrectly = self.numberOfPackages - correctlyDeliveredPkgs
        packagesNotDeliveredCorrectly_Normalised = packagesNotDeliveredCorrectly/self.numberOfPackages
        scoreContribution_PD = int(packagesNotDeliveredCorrectly_Normalised * 100)
        constraintViolationScore += scoreContribution_PD

        #check the number of unique batteries used in the solution
        batteriesUsed = constraintFuncs.countBatteriesUsed(drones)
        exceedingBatteries = max(batteriesUsed - self.maxBatteries , 0)
        scoreContribution_BU = 5 * exceedingBatteries
        constraintViolationScore += scoreContribution_BU

        #check if any drones run out of battery on trips
        droneDepletions = constraintFuncs.countDroneChargeDepletion(copy.deepcopy(drones)) 
        droneDepletions_Normalised = droneDepletions/len(drones)
        scoreContribution_DD = int(droneDepletions_Normalised * 100)
        constraintViolationScore += scoreContribution_DD

        #check if any drones are carrying too many packages
        overloadedTrips, numberOftrips = constraintFuncs.droneCargoCount(drones)
        overloadedTrips_Normalised = overloadedTrips/numberOftrips
        scoreContribution_LT = int(overloadedTrips_Normalised * 100)
        constraintViolationScore += scoreContribution_LT

        #check if any drones are carrying a payload which exceeds the drone capacity 
        overWeightedTrips = constraintFuncs.droneWeightCount(drones)
        overWeightedTrips_Normalised = overWeightedTrips/numberOftrips
        scoreContribution_WT = int(overWeightedTrips_Normalised * 100) 
        constraintViolationScore += scoreContribution_WT

        #check if drones start and finish at the depot
        notFinishing, notStarting = constraintFuncs.checkStartAndFinishPositions(drones)
        notFinishingOrStarting_Normalised = (notFinishing + notStarting) / numberOftrips * 2
        scoreContribution_FS = int(notFinishingOrStarting_Normalised * 100)
        constraintViolationScore += scoreContribution_FS

        #check if any charging stations are over filled
        overFilledChargingStations = constraintFuncs.chargingStationsOverCapacity(copy.deepcopy(drones))
        overFilledChargingStations_Normalisd = overFilledChargingStations/self.numberOfRechargingStations
        scoreContribution_OF = int(overFilledChargingStations_Normalisd * 100)
        constraintViolationScore += scoreContribution_OF

        #if any of the drone based constraint functions return False then 1000 penalty is applied
        # for function in droneConstraints: 
        #     if not function(copy.deepcopy(drones), detailed = False):
        #         Depot.batteriesHeld = originalState_depotBatteries
        #         print(f"function {function} violated")
        #         constraintViolationScore += 1000

        # if not constraintFuncs.countUniquePackagesDelivered(drones, detailed = False, NoOfPackages = self.numberOfPackages):
        #     print("violated1")
        #     constraintViolationScore += 1000
        
        # if not constraintFuncs.checkCustomerDemandsSatisfied(copy.deepcopy(drones), detailed = False, packages = self.packages):
        #     print("violated2")
        #     constraintViolationScore += 1000
        
        # if not constraintFuncs.countBatteriesUsed(drones, detailed = False, maxBatteries = self.maxBatteries):
        #     print("violated3")
        #     constraintViolationScore += 1000

        return constraintViolationScore

    '''
    returns a tuple -> the fitness score of the solution and the score contributions from hard constraints 
    '''
    def evaluate(self, solutionElements):
        originalState_depot = copy.deepcopy(Depot.batteriesHeld)
        drones = buildObjects(solutionElements, self.numberOfCustomers, self.nodes, self.packages)
        tripCount = 0 
        for drone in drones: 
            for trip in drone.trips:
                tripCount += 1
        maxDistanceTraveled = tripCount * params["dayLength"] * params["droneSpeed"]
        Depot.batteriesHeld = self.originalState_batteriesHeld
        maxScore = 1000
        noObjectives = 3 #the number of objectives listed in the initialiser 

        actualDistanceTraveled = self.actualDistanceCalculation(drones)
        actualLateness, maxLateness = self.actualLatenessCalculation(copy.deepcopy(drones)) #pass a copy of the list so that changing the drone variables don't affect the original list
        actualDronesUsed = len(drones)
        actualBatteriesUsed = constraintFuncs.countBatteriesUsed(drones)
        
        distanceNormalised = actualDistanceTraveled/maxDistanceTraveled
        latenessNormalised = actualLateness/maxLateness
        dronesNormalised = actualDronesUsed/self.maxDrones
        batteriesNormalised = actualBatteriesUsed/self.maxBatteries
        normalisedObjectiveValues = [distanceNormalised, dronesNormalised, batteriesNormalised, latenessNormalised]

        hardConstraintContribution = self.hardConstraintScore(drones)
        Depot.batteriesHeld = originalState_depot
        return (int(sum([obj * (maxScore/noObjectives) for obj in normalisedObjectiveValues]))) + hardConstraintContribution, hardConstraintContribution