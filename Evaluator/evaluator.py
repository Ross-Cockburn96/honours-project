import sys 
import argparse
sys.path.insert(0,"..")
from generatorObjects.drone import Drone
from generatorObjects.trip import Trip
from generatorObjects.action import Delivery, ChangeBattery, AtDepot
from generatorObjects.battery import Battery
from generatorObjects.package import Package
from generatorObjects.node import Depot, ChargingNode, CustomerNode

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


def buildNodes(problemElements): 
    problemCountIdx = 7 #first 5 elements are problem characteristics, 6 and 7 are always 0 for depot coordinates so set index to 8th element (idx 7) 
    depot = Depot()
    nodes.append(depot)
    numberBatteriesInDepot = problemElements[problemCountIdx]
    problemCountIdx += 1

    #extract number of batteries initialised to depot
    for _ in range(numberBatteriesInDepot):
        Depot.batteriesHeld.append(Battery.createWithID(problemElements[problemCountIdx]))
        problemCountIdx += 1

    #extract customer nodes from problem file
    for _ in range(numberOfCustomers): 
        customerNode = CustomerNode.rebuild(*problemElements[problemCountIdx:problemCountIdx+4])
        nodes.append(customerNode)
        problemCountIdx += 4

    #extract package data from problem file 
    for _ in range(numberOfPackages):
        package = Package(problemElements[problemCountIdx])
        problemCountIdx += 1
        package.weight = problemElements[problemCountIdx]
        problemCountIdx += 1
        package.destination = problemElements[problemCountIdx]
        problemCountIdx += 1
        packages.append(package)
    
    #extract recharging station from problem file 
    for _ in range(numberOfRechargeStations):
        chargeStation = ChargingNode(*problemElements[problemCountIdx:problemCountIdx+2])
        problemCountIdx += 2
        numberOfBatteries = problemElements[problemCountIdx] #the number of batteries initialised at this recharging station
        problemCountIdx += 1
        chargeStation.capacity = numberOfBatteries
        chargeStation.batteriesHeld = [Battery.createWithID(batteryID) for batteryID in problemElements[problemCountIdx:problemCountIdx + numberOfBatteries]]
        nodes.append(chargeStation)
        problemCountIdx += numberOfBatteries


def buildObjects(solutionElements):
    finished = False 
    solutionCountIdx = 1 #this index gives the number of trips in the first drone 
    
    #loops through the drones
    while solutionCountIdx < len(solutionElements):
        droneTrips = int(solutionElements[solutionCountIdx])
        drone = Drone()

        solutionCountIdx += 1

        #loops through the trips of the drone
        trips = []
        for _ in range(droneTrips):
            tripActions = int(solutionElements[solutionCountIdx])
            solutionCountIdx += 1

            actions = []
            #loops through the actions of a trip
            for _ in range(tripActions): 
                element = int(solutionElements[solutionCountIdx])
                if element == 0: 
                    action = AtDepot()
                    solutionCountIdx += 1
                elif element > numberOfCustomers: 
                    action = ChangeBattery(nodes[element], Battery.createWithID(solutionElements[solutionCountIdx + 1]), Battery.createWithID(solutionElements[solutionCountIdx + 2]))
                    solutionCountIdx += 3
                else: 
                    action = Delivery(nodes[element], solutionElements[solutionCountIdx + 1])
                    solutionCountIdx +=2
                actions.append(action)
            trips.append(Trip(actions))
        drones.append(Drone(trips))
 

with open(problem) as file:
    problemData = file.read()
    problemElements = problemData.split(",")
    problemElements = [int(e) for e in problemElements]
    numberOfCustomers = problemElements[2]
    numberOfRechargeStations = problemElements[4]
    numberOfPackages = problemElements[3]
    buildNodes(problemElements)

with open(solution) as file: 
    solutionData = file.read() 
    solutionElements = solutionData.split(",")
    solutionElements = [int(e) for e in solutionElements]
    buildObjects(solutionElements)
    

def checkPackagesDelivered():
    pass


with open(outputLocation, "w") as file:
    file.seek(0)
    file.write(f"PROBLEM FILE DATA\n------------------------------------------------------------\n")
    file.write(f"Maximum Number of drones available: {problemElements[0]}\n")
    file.write(f"Maximum Number of batteries available: {problemElements[1]}\n")
    file.write(f"Number of customers in problem file: {numberOfCustomers}\n")
    file.write(f"Number of packages to be delivered by drones: {numberOfPackages}\n")
    file.write(f"Number of recharging stations in the problem: {numberOfRechargeStations}\n\n")
    
    result = None
    file.write(f"CHECKING SOLUTION FILE FOR HARD CONSTRAINT VIOLATIONS\n------------------------------------------------------------\n")
    if int(solutionElements[0]) <= int(problemElements[0]):
        result = "PASS"
    else: 
        result = "FAIL"
    file.write(f"Drones used in solution: {solutionElements[0]}: {result}")
    result = checkPackagesDelivered()




