import argparse
import copy
from fileParsers.nodeBuilder import buildNodes
from .parameters import params 
from .individual import Individual 
from new_generator.parameters import Parameters
from generatorObjects.drone import Drone
from generatorObjects.action import Delivery, ChangeBattery, AtDepot
from generatorObjects.trip import Trip
from generatorObjects.battery import Battery
from generatorObjects.node import Node
from objectDeconstructors.phenotype import phenotype

parser = argparse.ArgumentParser()
parser.add_argument("--problem", "-p", nargs='?', type=str, help="Problem file address", required=True)
try:
    args = parser.parse_args()
    args = vars(args)
except IOError as msg:
    parser.error(str(msg))
    exit(0)

problem = args["problem"]

with open(problem) as file:
    problemData = file.read() 
    problemElements = problemData.split(",")
    problemElements = [int(e) for e in problemElements]

packages = []
nodes = []
chargingStations = [] 
nodes, packages = buildNodes(problemElements)

for node in nodes:
    if "ChargingNode" in str(type(node)):
        chargingStations.append(node)

chargingStations = list(filter(lambda x : len(x.batteriesHeld) > 0, chargingStations)) #ensure that only charging stations which have batteries are considered

params["numGenes"] = len(packages)
#genetic algorithm parameters
popsize = 1

def start():
    population = initialise()
    phenotype = decoder(population[0])
    with open ("solutionSample.txt", "w") as file:
        file.seek(0)
        string = ",".join([str(element) for element in phenotype])
        file.write(string)

def initialise():
    population = []
    for _ in range(popsize):
        individual = Individual()
        individual.initialise()
        population.append(individual)
    return population

def decoder(individual):
    drones = []
    droneActions = [] 

    drone = Drone()

    cargoTracker = 0
    weightTracker = 0
    distanceTracker = 0 

    for idx,gene in enumerate(individual.chromosome):
        package = packages[gene-1] #package ids start from 1
        destinationNode = nodes[package.destination] #node ids start from 0 
        newDelivery = Delivery(destinationNode, package) #create a new delivery acrion 
        droneActions.append(newDelivery)
        cargoTracker += 1 
        weightTracker += package.weight
        #if the new delivery made the trip invalid then remove it from trip and form the trip object
        if (cargoTracker > params["cargoSlotNum"]) or (weightTracker > params["cargoWeightLimit"]):
            
            #reset trackers
            cargoTracker = 1
            weightTracker = package.weight
                
            del droneActions[-1]
            #each trip will start and end at the depot 
            droneActions.insert(0, AtDepot())
            droneActions.append(AtDepot())
            #form the trip object
            trip = Trip(*droneActions)
            
            #action that was not taken on this trip will be part of the next trip
            droneActions = [newDelivery]
        
            tripDistance = Node.distanceCalc(*[action.node for action in trip.actions])
            #drone can't deliver this trip i
            if (drone.distanceLeft < tripDistance): 
                drones.append(drone)
                #start building new drone
                
                drone = Drone(trip)
            else:
                drone.trips.append(trip)
                drone.distanceLeft -= tripDistance
        if idx == params["numGenes"] - 1:
            droneActions.insert(0, AtDepot())
            droneActions.append(AtDepot())
            trip = Trip(*droneActions)
            tripDistance = Node.distanceCalc(*[action.node for action in trip.actions])
            #if drone can't deliver the trip add the drone and create and add new drone to finish decoding
            if (drone.distanceLeft < tripDistance): 
                drones.append(drone)
                drones.append(Drone(trip))
            else:
                drone.trips.append(trip)
                drones.append(drone)

    counter = 0

    includeChargingStations(drones)

    elements = phenotype(drones)
    return elements

def includeChargingStations(drones):
    # tripCounter = 0
    # val = []
    for drone in drones:
        for trip in drone.trips:
            # tripCounter += 1
            val.append(insertIntoTrip(trip, drone))
    # print(val.count(1))
    # print(tripCounter)
    # trip = drones[1].trips[0]
    # insertIntoTrip(trip, drones[0])
    # print(trip)
    # for drone in drones: 
    #  for trip in drone.trips: 
    #         insertIntoTrip(trip, drone)   


def calculateChargedValues(battery, currentTime):
    battery.batteryDistance += ((currentTime - battery.dockedTime)*Parameters.batteryChargingRate)
    return battery


def insertIntoTrip(trip, drone):
    isAddition = False
    startingCharge = drone.battery.batteryDistance #records what charge the battery hard at the start of the trip
    #print(f"starting charge is {startingCharge}")
    time = 0 
    stationHistory = [] #this keeps track of the charging stations that have been visited in a row. It is cleared as soon as a delivery is made. Stops infinite looping between 2 charging stations
    for idx, action in enumerate(trip.actions):
        if action in trip.actions[:-1]:
            distanceToTravel = Node.distanceFinder(action.node, action.nextAction.node)
            timeAtNextNode = time + (distanceToTravel/Parameters.droneSpeed) #the time that the next action on this drone would be completed
            #print(f"current node is {action.node} next node is {action.nextAction.node}")
            #if the current action is to change battery, then switch battery amount to battery selected
            if "ChangeBattery" in str(type(action)):
                #print(f"switching battery")
                drone.battery = action.batterySelected
                #update charging station to contain dropped off battery 
                swapIndex = action.node.batteriesHeld.index(action.batterySelected)
                action.node.batteriesHeld[swapIndex] = action.batteryDropped
            else:
                stationHistory = [] 

            #what the battery amount would be when arriving at the next node
            provisionalBatteryLevel = drone.battery.batteryDistance - distanceToTravel
            #print(f"distance to travel is {distanceToTravel}, battery charge left is {drone.battery.batteryDistance}")
            #if completing the next action will cause the drone to run out of battery
            if provisionalBatteryLevel < 0:
                otherChargingStations = list(filter(lambda x : x not in stationHistory, chargingStations))
                chargingStation = min(otherChargingStations, key=lambda x : int(Node.distanceFinder(x, action.node)))
                stationHistory.append(chargingStation)
                distanceToStation = Node.distanceFinder(action.node, chargingStation)
                #it is not possible for the drone to complete this trip
                #print(f"distance to station {distanceToStation}, distance left on battery {drone.battery.batteryDistance}") 
                if distanceToStation > drone.battery.batteryDistance:
                    print("no station found")
                    return 1
                drone.battery.batteryDistance -= distanceToStation
                timeAtNextNode = time + (distanceToStation / Parameters.droneSpeed) #next node will now be the charging station
                batteriesCopy = copy.deepcopy(chargingStation.batteriesHeld)
                #reduce list to only those batteries that exist at the station at the time the drone visits. 
                batteriesCopy = list(filter(lambda x, timeAtNextNode = timeAtNextNode: x.dockedTime <= timeAtNextNode if (x.dockedTime != None) else True, batteriesCopy))
                #return the highest charged battery after adjusting for the battery charge times
                highestCharged = max([calculateChargedValues(battery, timeAtNextNode) for battery in batteriesCopy], key = lambda x : x.batteryDistance)
                if highestCharged.batteryDistance > Parameters.batteryDistance:
                    highestCharged.batteryDistance = Parameters.batteryDistance
                
                realBattery = chargingStation.batteriesHeld[batteriesCopy.index(highestCharged)] #selects the unmodified battery object
                realBattery.batteryDistance = highestCharged.batteryDistance #update this battery's charge value

                #this action will cause the drone to drop off it's depleted battery and pick up the one with highest charge
                changeBatteryAction = ChangeBattery(chargingStation, drone.battery, realBattery)
                #print(trip)
                trip.insertAction(idx+1, changeBatteryAction)
                #print(trip)
                isAddition = True
        
            else:
                drone.battery.batteryDistance = provisionalBatteryLevel
        time = timeAtNextNode   
    return 2 
    #if there has been an addition to the trip start calculating again
    # if isAddition and run < 2:
    #     insertIntoTrip(trip, drone, run+1)




start()

