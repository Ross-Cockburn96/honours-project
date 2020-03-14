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

nodes, packages = buildNodes(problemElements)

print(f"length of packages is {len(packages)}")
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
            
            print(idx)
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
            print(f"drone actions before delete is {droneActions}")
            droneActions = [newDelivery]
        
            tripDistance = Node.distanceCalc(*[action.node for action in trip.actions])
            #drone can't deliver this trip i
            if (drone.distanceLeft < tripDistance): 
                drones.append(drone)
                print(f"forming drone index {idx}")
                print(f"actions on next trip are {droneActions}")
                for trip2 in drone.trips:
                    print(f"forming with {trip2}")
                #start building new drone
                
                drone = Drone(trip)
            else:
                drone.trips.append(trip)
                print(f"added trip {idx} {len(trip.actions)}")
                drone.distanceLeft -= tripDistance
        if idx == params["numGenes"] - 1:
            print(f"final")
            droneActions.insert(0, AtDepot())
            droneActions.append(AtDepot())
            trip = Trip(*droneActions)
            tripDistance = Node.distanceCalc(*[action.node for action in trip.actions])
            #if drone can't deliver the trip add the drone and create and add new drone to finish decoding
            if (drone.distanceLeft < tripDistance): 
                print(f"new drone")
                drones.append(drone)
                drones.append(Drone(trip))
            else:
                print(f"old drone")
                drone.trips.append(trip)
                drones.append(drone)

    counter = 0
    print(f"chromosome is {individual.chromosome}")
    for drone in drones:
        for trip in drone.trips:
            for action in trip.actions: 
                if "Delivery" in str(type(action)):
                    print(f"{action.package.id}  {nodes[action.package.destination]}")
                    
                    counter += 1
    print(counter)
    elements = phenotype(drones)
    return elements

start()

