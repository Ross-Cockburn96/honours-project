import argparse
import copy
import random
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
from evaluator.constraintFuncs import *



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
#add the depot to charging stations 
chargingStations.append(nodes[0])
params["numGenes"] = len(packages)
#genetic algorithm parameters
popsize = 10

def start():
    population = initialise()
    evaluatePopulation(population)
    #individual = Individual()
    #individual.chromosome = [5,1,2,3,4,7,9,6,8,10,11,13,12,14,15,18,16,19,17,20,22,21,24,25,26,23,30,31,28,27,29,32,36,35,34,33,37,40,39,41,38,44,42,43,45,50,47,48,46,49,51,53,55,52,54,57,56,59,60,61,62,58,63,64,65,67,68,66,71,70,69,75,76,74,72,73,80,81,79,78,77,89,87,88,90,92,94,91,93,95,96,97,98,99,100,84,86,82,83,85]
    
    #phenotype, _ = decoder(population)
    for _ in range(5000):
        parent1 = tournamentSelect(population)
        parent2 = tournamentSelect(population)
        
        child = crossover(parent1, parent2)
        _,drones = decoder(child)
        child.drones = drones
        child.fitness = evaluate(child.drones)

        replace(child, population)

        best = min(population, key = lambda x : x.fitness)
        print([i.fitness for i in population])
        print(f"BEST IN ITERATION: {best.fitness}")
    # with open ("solutionSample.txt", "w") as file:
    #     print("writing to sample")
    #     file.seek(0)
    #     string = ",".join([str(element) for element in phenotype])
    #     file.write(string)
def initialise():
    population = []
    for _ in range(popsize):
        individual = Individual()
        individual.initialise()
        population.append(individual)
    return population

def evaluatePopulation(population):
    for individual in population: 
        _, drones = decoder(individual)
        individual.drones = drones
        individual.fitness = evaluate(drones)
    
    for individual in population:
        print(f"fitness is {individual.fitness}")

def norm(x, xMax):
    return x/xMax

def evaluate(drones):
    numDepletions = countDroneChargeDepletion(drones)
    actualDistanceTraveled = 0
    maxDrones = problemElements[0]
    dayLength = 28800
    droneSpeed = 10
    maxDistanceTraveled = maxDrones * dayLength * droneSpeed #max distance possible is if all drones are used and are travelling all day without stopping 
    maxBatteries = problemElements[1]
    for drone in drones:
        for trip in drone.trips:
            actualDistanceTraveled += Node.distanceCalc(*[action.node for action in trip.actions])
    
    actualDronesUsed = len(drones)
    actualBatteriesUsed = countBatteriesUsed(drones)
    numDronesDepleted = countDroneChargeDepletion(drones)

    maxScore = 1000
    numObjectives = 4
    scoreRatio = maxScore/4
    distanceNorm = norm(actualDistanceTraveled, maxDistanceTraveled)
    dronesNorm = norm(actualDronesUsed, maxDrones)
    batteriesNorm = norm(actualBatteriesUsed, maxBatteries)
    depletionNorm = norm(numDronesDepleted, actualDronesUsed)

    return int((distanceNorm * scoreRatio) + (dronesNorm * scoreRatio) + (batteriesNorm * scoreRatio) + (depletionNorm * scoreRatio))

def tournamentSelect(population):
    competitors = []
    for idx in range(params["tournamentSize"]):
        individual = population[random.randrange(len(population))]
        competitors.append(individual)
    
    winner = min(competitors, key=lambda x : x.fitness)
    return copy.deepcopy(winner)

def crossover(parent1, parent2):
    child = Individual()
    geneA = random.randrange(params["numGenes"])
    geneB = random.randrange(params["numGenes"])

    startGene = min(geneA,geneB)
    endGene = max(geneA, geneB)

    for i in range(startGene, endGene):
        child.chromosome[i] = parent1.chromosome[i]
    
    for i in range(startGene):
        child.chromosome[i] = parent2.chromosome[i]
    
    for i in range(endGene, params["numGenes"]):
        child.chromosome[i] = parent2.chromosome[i]
    
    return child

def replace(child, population):
    worst = min(population, key=lambda x : x.fitness)
    if child.fitness < worst.fitness:
        population[population.index(worst)] = child
'''
takes indirect genotype and builds the phenotype, returns the phenotype in it's raw format (elements) and in it's object format (drones)
'''
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
        newDelivery = Delivery(destinationNode, package) #create a new delivery action 
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
    #elements = phenotype(drones)
    return elements, drones

def includeChargingStations(drones):
    for drone in drones:
        for trip in drone.trips:
            if insertIntoTrip(trip, drone) == -1: 
                break

    # for trip in drones[0].trips[:-2]:
    #     insertIntoTrip(trip, drones[0])
   
    # print(trip)
    # for drone in drones: 
    #  for trip in drone.trips: 
    #         insertIntoTrip(trip, drone)   


def calculateChargedValues(battery, currentTime):
    if battery.dockedTime != None:
        battery.batteryDistance += ((currentTime - battery.dockedTime)*Parameters.batteryChargingRate)
    return battery


def insertIntoTrip(trip, drone):
    isAddition = False
    startingCharge = drone.battery.batteryDistance #records what charge the battery hard at the start of the trip
    #print(f"starting charge is {startingCharge}")
    stationHistory = [] #this keeps track of the charging stations that have been visited in a row. It is cleared as soon as a delivery is made. Stops infinite looping between 2 charging stations
    for idx, action in enumerate(trip.actions):
        if action in trip.actions[:-1]:
            distanceToTravel = Node.distanceFinder(action.node, action.nextAction.node)
            timeAtNextNode = drone.time + (distanceToTravel/Parameters.droneSpeed) #the time that the next action on this drone would be completed
            #print(f"current node is {action.node} next node is {action.nextAction.node}")
            #if the current action is to change battery, then switch battery amount to battery selected
            if "ChangeBattery" in str(type(action)):
                #print(f"switching battery")
                drone.battery.dockedTime = drone.time
                drone.battery = action.batterySelected
                #update charging station to contain dropped off battery 
                swapIndex = action.node.batteriesHeld.index(action.batterySelected)
                action.node.batteriesHeld[swapIndex] = action.batteryDropped
            else:
                stationHistory = [] #clear station history when an action that isn't a change battery action is carried out

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
                    #print("no station found")
                    return -1
                drone.battery.batteryDistance -= distanceToStation
                timeAtNextNode = drone.time + (distanceToStation / Parameters.droneSpeed) #next node will now be the charging station
                batteriesCopy = copy.deepcopy(chargingStation.batteriesHeld)
                #reduce list to only those batteries that exist at the station at the time the drone visits. 
                # print(batteriesCopy)
                # print(drone.time)
                # for battery12 in batteriesCopy: 
                #     print(battery12.dockedTime)
                batteriesCopy = list(filter(lambda x, timeAtNextNode = timeAtNextNode: x.dockedTime <= timeAtNextNode if (x.dockedTime != None) else True, batteriesCopy))
                #print(batteriesCopy)
                #check the list is not empty
                if batteriesCopy:
                    #return the highest charged battery after adjusting for the battery charge times
                    highestCharged = max([calculateChargedValues(battery, timeAtNextNode) for battery in batteriesCopy], key = lambda x : x.batteryDistance)
                else: 
                    #drone is depleted
                    #print(f"finishing")
                    return -1
                if highestCharged.batteryDistance > Parameters.batteryDistance:
                    highestCharged.batteryDistance = Parameters.batteryDistance
                realBattery = chargingStation.batteriesHeld[batteriesCopy.index(highestCharged)] #selects the unmodified battery object
                realBattery.batteryDistance = highestCharged.batteryDistance #update this battery's charge value

                #this action will cause the drone to drop off it's depleted battery and pick up the one with highest charge
                changeBatteryAction = ChangeBattery(chargingStation, drone.battery, realBattery)
                if ("AtDepot" in str(type(action))) and (chargingStation.getCoords() == (0,0)):
                    #print("replacing at depot with charging node")
                    del trip.actions[0]
                    trip.insertAction(0, changeBatteryAction)
                #print(trip)
                trip.insertAction(idx+1, changeBatteryAction)
                #print(trip)
                isAddition = True
        
            else:
                drone.battery.batteryDistance = provisionalBatteryLevel
        drone.time = timeAtNextNode   
    return 2 
    #if there has been an addition to the trip start calculating again
    # if isAddition and run < 2:
    #     insertIntoTrip(trip, drone, run+1)




start()

