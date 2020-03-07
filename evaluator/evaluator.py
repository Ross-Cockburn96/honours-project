import sys 
import argparse
sys.path.insert(0,"..")
from generatorObjects.drone import Drone
from generatorObjects.trip import Trip
from generatorObjects.action import Delivery, ChangeBattery, AtDepot
from generatorObjects.battery import Battery
from generatorObjects.package import Package
from generatorObjects.node import Depot, ChargingNode, CustomerNode, Node

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

#fixed properties
dayLength = 28800
droneSpeed = 10 #m/s

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
        print(f"drone trips: {droneTrips}")
        solutionCountIdx += 1

        #loops through the trips of the drone
        trips = []
        for _ in range(droneTrips):
            tripActions = int(solutionElements[solutionCountIdx])
            print(f"actions in trip {tripActions}")
            solutionCountIdx += 1

            actions = []
            #loops through the actions of a trip
            for _ in range(tripActions): 
                element = int(solutionElements[solutionCountIdx])
                print(element)
                if element == 0: 
                    action = AtDepot()
                    solutionCountIdx += 1
                elif element > numberOfCustomers: 
                    print(f"LENGTH of nodes is {len(nodes)} trying element {element}")
                    action = ChangeBattery(nodes[element], Battery.createWithID(solutionElements[solutionCountIdx + 1]), Battery.createWithID(solutionElements[solutionCountIdx + 2]))
                    solutionCountIdx += 3
                else: 
                    action = Delivery(nodes[element], packages[solutionElements[solutionCountIdx + 1]-1]) #package ids start at 1 but package list index starts at 0 so minus one from the id in the solution to get correct package
                    solutionCountIdx +=2
                actions.append(action)
            trips.append(Trip(*actions))
        drones.append(Drone(*trips))
        #print(f"len of rebuilt drone trips is {len(drones[0].trips)}")
 

with open(problem) as file:
    problemData = file.read()
    problemElements = problemData.split(",")
    problemElements = [int(e) for e in problemElements]
    numberOfCustomers = problemElements[2]
    numberOfRechargeStations = problemElements[4]
    numberOfPackages = problemElements[3]
    maxBatteriesAvailable = problemElements[1]
    buildNodes(problemElements)
    print(len(nodes))

with open(solution) as file: 
    solutionData = file.read() 
    solutionElements = solutionData.split(",")
    solutionElements = [int(e) for e in solutionElements]
    buildObjects(solutionElements)
    

def countUniquePackagesDelivered():
    packages = [] 

    #create a list of all packages delivered in the solution
    for drone in drones:
        for action in drone.getAllActions():
            if "Delivery" in str(type(action)):
                packages.append(action.package.id)

    return len(set(packages))

def countBatteriesUsed():
    batteries = []
    #create a list of all batteries used in the solution
    batteries.extend(Depot.batteriesHeld)
    for drone in drones:
        batteries.append(drone.battery)
        for action in drone.getAllActions():
            if "ChangeBattery" in str(type(action)):
                batteries.append(action.batterySelected)
    batteries.sort(key=lambda x : x.id)
    return len(set(batteries))

def countDroneChargeDepletion(): 
    numberOfDepletions = 0
    for drone in drones: 
        if Node.distanceCalc(*[action.node for action in drone.getAllActions()]) > dayLength * droneSpeed:
            print("NEED TO CREATE A NEW BLOODY DRONE FFS1")

    for drone in drones: 
        for trip in drone.trips: 
            for action in trip.actions[1:]: 
                if "ChangeBattery" in str(type(action)):
                    print()
                    print(f"changing battery from battery with {drone.battery.batteryDistance}")
                    drone.battery = action.batterySelected
                    print(f"to {drone.battery.batteryDistance}")
                    print()
                    #may need to calculate the charge of the battery selected
                distanceTraveled = Node.distanceFinder(action.node, action.prevAction.node)
                drone.battery.batteryDistance -= distanceTraveled
                print(drone.battery.batteryDistance)
                if drone.battery.batteryDistance < 0: 
                    numberOfDepletions += 1
                    break
            else:
                continue 
            break
    return numberOfDepletions

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
    file.write(f"Packages delivered by solution => {packagesDelivered}/{numberOfPackages}: {result}\n")
    
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
    file.write(f"Number of drones that ran out of power in solution => {batteriesOutOfCharge}/{len(drones)}: {result}")

