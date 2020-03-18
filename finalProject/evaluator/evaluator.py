import sys 
import argparse
from fileParsers.nodeBuilder import buildNodes
from fileParsers.objectBuilder import buildObjects
from generatorObjects.node import Depot, Node
#from context import generatorObjects

parser = argparse.ArgumentParser()
parser.add_argument("--solution", "-s", nargs='?', type=str, help="Solution file address", required=True)
parser.add_argument("--problem", "-p", nargs='?', type=str, help="Problem file address", required=True)
parser.add_argument("--output", "-o", nargs='?', type=str, default="output.txt", help="Output file write address")

try:
    args = parser.parse_args()
    args = vars(args)
except IOError as msg:
    parser.error(str(msg)) 
    exit(0)

solution = args["solution"]
problem = args["problem"]
outputLocation = args["output"]

#Objects
drones = []
nodes = [] #this will be a collection of all nodes - depot, customer and recharge as their id in the solution file will correlate to the index in list 
packages = [] 

#Problem Characteristics
numberOfCustomers = None
numberOfRechargeStations = None
numberOfPackages = None
maxBatteriesAvailable = None

#objective constants - change depending on what problem instance is used but remain constant for each solution evaluated
maxDistanceTraveled = None
maxDrones = None 
maxBatteries = None 

dronesUsedMultiplier = None #multipliers used to make each component of the objective function equally important
batteriesUsedMultiplier = None 


#fixed properties
dayLength = 28800
droneSpeed = 10 #m/s
droneCargoLimit = 5
droneWeightLimit = 30 #lb

with open(problem) as file:
    problemData = file.read()
    problemElements = problemData.split(",")
    problemElements = [int(e) for e in problemElements]
    numberOfCustomers = problemElements[2]
    numberOfRechargeStations = problemElements[4]
    numberOfPackages = problemElements[3]
    maxBatteriesAvailable = problemElements[1]
    nodes, packages = buildNodes(problemElements)

with open(solution) as file: 
    solutionData = file.read() 
    solutionElements = solutionData.split(",")
    solutionElements = [int(e) for e in solutionElements]
    drones = buildObjects(solutionElements, numberOfCustomers, nodes, packages)
    

def countUniquePackagesDelivered():
    packages = [] 

    #create a list of all packages delivered in the solution
    for drone in drones:
        for action in drone.getAllActions():
            if "Delivery" in str(type(action)):
                packages.append(action.package.id)
    return len(set(packages))

def checkCustomerDemandsSatisfied():
    packageDemandDic = dict(zip([pkg.id for pkg in packages], [pkg.destination for pkg in packages]))
    packagesDeliveredCorrectly = 0
    for drone in drones:
        for trip in drone.trips:
            for action in trip.actions:
                if "Delivery" in str(type(action)):
                    if action.node.id == packageDemandDic[action.package.id]:
                        packagesDeliveredCorrectly += 1
    
    return packagesDeliveredCorrectly

def countBatteriesUsed():
    batteries = []
    #create a list of all batteries used in the solution
    batteries.extend(Depot.batteriesHeld)
    for drone in drones:
        batteries.append(drone.battery)
        for action in drone.getAllActions():
            if "ChangeBattery" in str(type(action)):
                print(f"change battery action: {action}, {type(action)}")
                batteries.append(action.batterySelected)
    batteries.sort(key=lambda x : x.id)
    return len(set(batteries))

def countDroneChargeDepletion(): 
    numberOfDepletions = 0
    for drone in drones: 
        for trip in drone.trips: 
            for action in trip.actions[1:]: 
                if "Delivery" in str(type(action)) or "AtDepot" in str(type(action)):
                    distanceTraveled = Node.distanceFinder(action.node, action.prevAction.node)
                    drone.battery.batteryDistance -= distanceTraveled
                else:
                    drone.battery = action.batterySelected
                    #may need to calculate the charge of the battery selected
                if drone.battery.batteryDistance < 0: 
                    numberOfDepletions += 1
                    break
            else:
                continue 
            break
    return numberOfDepletions

def droneCargoCount():
    numberOfTripsWithTooManyPackages = 0
    tripCount = 0
    for drone in drones:
        for trip in drone.trips:
            tripCount += 1
            packageCount = 0
            for action in trip.actions:
                if "Delivery" in str(type(action)):
                    packageCount += 1
            if packageCount > 5: 
                numberOfTripsWithTooManyPackages += 1
    return numberOfTripsWithTooManyPackages, tripCount

def droneWeightCount():
    numberOfTripswithTooHeavyPackages = 0 
    for drone in drones:
        for trip in drone.trips:
            weightTotal = 0
            for action in trip.actions:
                if "Delivery" in str(type(action)):
                    weightTotal += action.package.weight
            if weightTotal > 30: 
                numberOfTripswithTooHeavyPackages += 1
    return numberOfTripswithTooHeavyPackages

def checkStartAndFinishPositions(): 
    tripsNotStartingAtDepot = 0 
    tripsNotFinishingAtDepot = 0 
    for drone in drones:
        for trip in drone.trips: 
            if trip.actions[0].node.getCoords() != (0,0):
                tripsNotStartingAtDepot += 1
            if trip.actions[-1].node.getCoords() != (0,0):
                tripsNotFinishingAtDepot += 1
    
    return tripsNotFinishingAtDepot, tripsNotStartingAtDepot
            
def initialiseObjectiveConstants():
    global maxDrones, maxDistanceTraveled, maxBatteries, dronesUsedMultiplier, batteriesUsedMultiplier
    maxDrones = problemElements[0]
    maxDistanceTraveled = maxDrones * dayLength * droneSpeed #max distance possible is if all drones are used and are travelling all day without stopping 
    maxBatteries = maxBatteriesAvailable

    dronesUsedMultiplier = maxDistanceTraveled/maxDrones
    batteriesUsedMultiplier = maxDistanceTraveled/maxBatteries

def evaluateSolutionFitness(batteriesUsed):
    actualDistanceTraveled = 0 
    for drone in drones:
        for trip in drone.trips:
            actualDistanceTraveled += Node.distanceCalc(*[action.node for action in trip.actions])

    actualDronesUsed = solutionElements[0]
    actualBatteriesUsed = batteriesUsed
    return (actualDistanceTraveled + actualDronesUsed * dronesUsedMultiplier + actualBatteriesUsed * batteriesUsedMultiplier)

with open(outputLocation, "w") as file:
    file.seek(0)
    file.write(f"PROBLEM FILE DATA\n------------------------------------------------------------\n")
    file.write(f"Maximum Number of drones available: {problemElements[0]}\n")
    file.write(f"Maximum Number of batteries available: {maxBatteriesAvailable}\n")
    file.write(f"Number of customers in problem file: {numberOfCustomers}\n")
    file.write(f"Number of packages to be delivered by drones: {numberOfPackages}\n")
    file.write(f"Number of recharging stations in the problem: {numberOfRechargeStations}\n\n")
    
    result = None
    file.write(f"CHECKING SOLUTION FILE FOR HARD CONSTRAINT VIOLATIONS\n------------------------------------------------------------\n")
    if int(solutionElements[0]) <= int(problemElements[0]):
        result = "PASS"
    else: 
        result = "FAIL"
    file.write(f"Drones used in solution => {solutionElements[0]}: {result}\n")
    
    packagesDelivered = countUniquePackagesDelivered()
    if packagesDelivered == numberOfPackages:
        result == "PASS"
    else:
        result = "FAIL"
    file.write(f"Packages scheduled for delivery by solution => {packagesDelivered}/{numberOfPackages}: {result}\n")

    correctlyDeliveredPackages = checkCustomerDemandsSatisfied()
    if correctlyDeliveredPackages == numberOfPackages:
        result = "PASS"
    else:
        result = "FAIL"
    file.write(f"Packages delivered to correct customer => {correctlyDeliveredPackages}/{numberOfPackages}: {result}\n")
    
    batteriesUsed = countBatteriesUsed()
    if batteriesUsed > maxBatteriesAvailable:
        result = "FAIL"
    else:
        result = "PASS"
    file.write(f"Number of batteries used by solution => {batteriesUsed}, maximum available is {maxBatteriesAvailable}: {result}\n")

    batteriesOutOfCharge = countDroneChargeDepletion()
    if batteriesOutOfCharge > 0: 
        result = "FAIL"
    else:
        result = "PASS"
    file.write(f"Number of drones that ran out of power in solution => {batteriesOutOfCharge}/{len(drones)}: {result}\n")

    overloadedTrips, numOfTrips = droneCargoCount()
    if overloadedTrips > 0: 
        result = "FAIL" 
    else: 
        result = "PASS" 
    file.write(f"Number of trips that overloaded the drone cargo limit => {overloadedTrips}/{numOfTrips}: {result}\n")

    overweightedTrips = droneWeightCount()
    if overweightedTrips > 0:
        result = "FAIL"
    else:
        result = "PASS"
    file.write(f"Number of trips that contain a cargo that is too heavy for their drone => {overweightedTrips}/{numOfTrips}: {result}\n")
    
    notFinishing, notStarting = checkStartAndFinishPositions()
    if notStarting > 0: 
        result = "FAIL" 
    else:
        result = "PASS"
    file.write(f"Number of trips where drone does not start at the depot => {notStarting}/{numOfTrips}: {result}\n")

    if notFinishing > 0:
        result = "FAIL"
    else:
        result = "PASS"
    file.write(f"Number of trips where drone does finish at the depot => {notFinishing}/{numOfTrips}: {result}\n")
    
    file.write(f"\nFITNESS SCORE OF SOLUTION\n------------------------------------------------------------\n")
    initialiseObjectiveConstants()
    score = evaluateSolutionFitness(batteriesUsed)
    
    #file.write(f"{score:.20f}\n")
    file.write(f"{int(score)}\n")