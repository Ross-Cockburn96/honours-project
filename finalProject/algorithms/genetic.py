import argparse
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
    if "ChargingStation" in str(type(node)):
        chargingStations.append(node)


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
    for drone in drones: 
        for trip in trip: 
            tripDistance = Node.distanceCalc(*[action.node for action in trip.actions])
            #if trip will cause battery to run out of charge, add 
            while drone.battery.batteryDistance - tripDistance < 0: 
            if drone.battery.batteryDistance - tripDistance < 0: 
                for action in trip.actions[1:]:

def insertIntoTrip(trip):
    for idx, action in enumerate(trip.actions):
        if action in trip.actions[:-1]:
            if "Delivery" in str(type(action)) or "AtDepot" in str(type(action)):
                distanceToTravel = Node.distanceFinder(action.node, action.nextAction.node)
                provisionalValue = drone.battery.batteryDistance - distanceToTravel
            else:
                drone.battery = action.batterySelected
            if provisionalValue < 0:
                timeAccessingChargeStation = (Parameters.dayLength - drone.distanceLeft) / Parameters.droneSpeed
                chargingStation = min(chargingStations, key=lambda x : int(Node.distanceFinder(x, action.node)))
                distanceToStation = Node.distanceFinder(action.node, chargingStation)
                
                #this action will cause the drone to drop off it's depleted battery and pick up the one with highest charge
                changeBatteryAction = ChangeBattery(chargingStation, drone.battery, max(chargingStation.batteriesHeld, key=lambda x : x.batteryDistance))
                trip.insert(idx, chargingStation)


start()

