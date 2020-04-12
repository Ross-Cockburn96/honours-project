import sys 
import argparse
import copy
from .score import Fitness
from fileParsers.nodeBuilder import buildNodes
from fileParsers.objectBuilder import buildObjects
from generatorObjects.node import Depot, Node
from .constraintFuncs import * 
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

fitnessEvaluator = Fitness(problemElements) #used to calculate the fitness score of the solution file

with open(solution) as file: 
    solutionData = file.read() 
    solutionElements = solutionData.split(",")
    solutionElements = [int(e) for e in solutionElements]
    drones = buildObjects(solutionElements, numberOfCustomers, nodes, packages)

actualDistanceTraveled = 0
for drone in drones:
    for trip in drone.trips:
        actualDistanceTraveled += Node.distanceCalc(*[action.node for action in trip.actions])

maxDistanceTraveled = problemElements[0] * params["dayLength"] * params["droneSpeed"]

dronesCopy = copy.deepcopy(drones)
lateness = 0
lateCounter = 0 
regCounter = 0 
for drone in dronesCopy:
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
lateness = int(lateness)

maxLateness = 0
numberOfCustomers = problemElements[2]
#start at first customer node 
index = 7 
for _ in range(numberOfCustomers): 
    closeTime = problemElements[index + 3]
    maxLateness += params["dayLength"] - closeTime
    index += 4

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
    
    packagesDelivered = countUniquePackagesDelivered(drones)
    if packagesDelivered == numberOfPackages:
        result == "PASS"
    else:
        result = "FAIL"
    file.write(f"Packages scheduled for delivery by solution => {packagesDelivered}/{numberOfPackages}: {result}\n")
    
    correctlyDeliveredPackages = checkCustomerDemandsSatisfied(copy.deepcopy(drones), packages)
    if correctlyDeliveredPackages == numberOfPackages:
        result = "PASS"
    else:
        result = "FAIL"
    file.write(f"Packages delivered successfully to correct customer => {correctlyDeliveredPackages}/{numberOfPackages}: {result}\n")
    
    batteriesUsed = countBatteriesUsed(drones)
    if batteriesUsed > maxBatteriesAvailable:
        result = "FAIL"
    else:
        result = "PASS"
    file.write(f"Number of batteries used by solution => {batteriesUsed}, maximum available is {maxBatteriesAvailable}: {result}\n")
    
    batteriesOutOfCharge = countDroneChargeDepletion(copy.deepcopy(drones)) #calculating depletion points changed variables of drones so deep copy for safety
    if batteriesOutOfCharge > 0: 
        result = "FAIL"
    else:
        result = "PASS"
    file.write(f"Number of drones that ran out of power in solution => {batteriesOutOfCharge}/{len(drones)}: {result}\n")

    overloadedTrips, numOfTrips = droneCargoCount(drones)
    if overloadedTrips > 0: 
        result = "FAIL" 
    else: 
        result = "PASS" 
    file.write(f"Number of trips that overloaded the drone cargo limit => {overloadedTrips}/{numOfTrips}: {result}\n")

    overweightedTrips = droneWeightCount(drones)
    if overweightedTrips > 0:
        result = "FAIL"
    else:
        result = "PASS"
    file.write(f"Number of trips that contain a cargo that is too heavy for their drone => {overweightedTrips}/{numOfTrips}: {result}\n")
    
    notFinishing, notStarting = checkStartAndFinishPositions(drones)
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
    
    overFilledChargingStations = chargingStationsOverCapacity(copy.deepcopy(drones))
    if overFilledChargingStations > 0:
        result = "FAIL"
    else:
        result = "PASS"
    file.write(f"Number of charging stations with batteries exceeding capacity => {overFilledChargingStations}/{numberOfRechargeStations}: {result}\n")
    
    file.write(f"\nOBJECTIVE FUNCTION BREAKDOWN\n------------------------------------------------------------\n")
    file.write(f"Distance travelled out total possible distance => {actualDistanceTraveled}/{maxDistanceTraveled}\n")
    file.write(f"Delivery lateness out of total possible lateness => {lateness}/{maxLateness}\n")
    file.write(f"Drones used out of total drones available => {len(drones)}/{problemElements[0]}\n")
    file.write(f"Batteries used out of total batteries available => {batteriesUsed}/{problemElements[1]}\n")
    
    file.write(f"\nSOLUTION SCORE\n------------------------------------------------------------\n")    
    score, hard = fitnessEvaluator.evaluate(solutionElements)
    #file.write(f"{score:.20f}\n")
    file.write(f"Fitness: {int(score)}\n")
    file.write(f"Hard Constraint Score: {int(hard)}\n")