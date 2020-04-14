import argparse
import copy
import random
from evaluator.score import Fitness
from fileParsers.nodeBuilder import buildNodes
from .parameters import params 
from .individual import Individual 
from new_generator.parameters import Parameters
from generatorObjects.drone import Drone
from generatorObjects.action import Delivery, ChangeBattery, AtDepot
from generatorObjects.trip import Trip
from generatorObjects.battery import Battery
from generatorObjects.node import Node, Depot
from objectDeconstructors.phenotype import phenotype
import matplotlib.pyplot as plt 

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
fitnessEvaluator = Fitness(problemElements)

for node in nodes:
    if ("ChargingNode" in str(type(node))) or (node.id == problemElements[2] + 1):
        chargingStations.append(node)
    
chargingStations = list(filter(lambda x : len(x.batteriesHeld) > 0, chargingStations)) #ensure that only charging stations which have batteries are considered
params["numGenes"] = len(packages)

def start():
    maxIterations = 0
    population = initialise()
    evaluatePopulation(population)

    for _ in range(maxIterations): 
        newIndividual = Individual()
        newIndividual.initialise()
        newIndividual.phenotype, newIndividual.drones = decoder(newIndividual)
        newIndividual.fitness, newIndividual.hardConstraintFitness = fitnessEvaluator.evaluate(newIndividual.phenotype)
        print(newIndividual.hardConstraintFitness)
        replace(newIndividual, population)
         #list containing all members of the population that satisfy hard constraints
        filteredPop = list(filter(lambda x : x.hardConstraintFitness == 0, population))
        #if the list is empty then the best solution is the one that violates the constraints the least 
        if not filteredPop:
            best = min(population, key = lambda x : x.hardConstraintFitness)
        else:
    
            best = min(filteredPop, key = lambda x : x.fitness)
        print([i2.hardConstraintFitness for i2 in population])
        print([i.fitness for i in population])
    filteredFinalPop = list(filter(lambda x : x.hardConstraintFitness == 0, population))
    if not filteredFinalPop:
        best = min(population, key = lambda x : x.hardConstraintFitness)
    else:
        best = min(filteredFinalPop, key = lambda x : x.fitness)
    print(f"best found is {best.fitness}, {best.hardConstraintFitness}")
    with open ("solutionSample.txt", "w") as file:
        print("writing to sample")
        file.seek(0)
        string = ",".join([str(element) for element in best.phenotype])
        file.write(string)
def initialise():
    population = []
    for _ in range(params["popSize"]):
        individual = Individual()
        individual.initialise()
        population.append(individual)
    return population

def evaluatePopulation(population):
    for individual in population: 
        individual.phenotype, individual.drones = decoder(individual)
        individual.fitness, individual.hardConstraintFitness = fitnessEvaluator.evaluate(individual.phenotype)
    for individual in population:
        print(f"fitness is {individual.fitness}, hardConstraintFitness is {individual.hardConstraintFitness}")

def replace(child, population):
    worst = max(population, key=lambda x : x.hardConstraintFitness)
    print(f"worst found is {worst.hardConstraintFitness}")
    #if the worst has hard constraint fitness of 0 then all population has satisfied the hard constraints 
    if worst.hardConstraintFitness == 0 and (child.hardConstraintFitness == 0): 
        worst = max(population, key=lambda x : x.fitness)
        if (child.fitness < worst.fitness):
            population[population.index(worst)] = child
    else:
        if child.hardConstraintFitness < worst.hardConstraintFitness:
            population[population.index(worst)] = child
'''
takes indirect genotype and builds the phenotype, returns the phenotype in it's raw format (elements) and in it's object format (drones)
'''
def decoder(individual):
    Battery.idCounter = 1
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

#this function adds charging stations to each trip and restores the states back to initialised values including the charging stations
def includeChargingStations(drones):
    global chargingStations
    originalState_depotBatteries = copy.deepcopy(Depot.batteriesHeld)
    originalState_chargingStations = copy.deepcopy(chargingStations) #charging station states change in the insertIntoTrip function so keep original to restore from 
    originalState_chargingStationDict = {station.id : station for station in originalState_chargingStations}
    originalState_droneBatteries = [copy.deepcopy(d.battery) for d in drones]
    for drone in drones:
        for trip in drone.trips:
            if insertIntoTrip(trip, drone) == -1: 
                print(f"ABORTED")
                break
    
    
    Depot.batteriesHeld = copy.deepcopy(originalState_depotBatteries)
    #restore pointers in changebattery actions to original state stations
    for drone in drones:
        for trip in drone.trips: 
            for action in trip.actions: 
                if "ChangeBattery" in str(type(action)): 
                    for b in action.node.batteriesHeld: 
                        b.reset()
                    action.batteryDropped.reset()
                    action.batterySelected.reset()

    #restore charging station states
    chargingStations = copy.deepcopy(originalState_chargingStations)
    
    #restore drone battery states
    for idx, drone in enumerate(drones):
        drone.battery = copy.copy(originalState_droneBatteries[idx])
    
    
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
            distanceToTravel = round(Node.distanceFinder(action.node, action.nextAction.node))
            #the time that the next action on this drone would be completed
            timeAtNextNode = drone.time + (distanceToTravel/Parameters.droneSpeed) 
            #if the current action is to change battery, then switch battery amount to battery selected
            if "ChangeBattery" in str(type(action)):
                drone.battery.dockedTime = drone.time
                drone.battery = action.batterySelected
                if drone.battery.dockedTime != None: 
                    drone.battery.batteryDistance = min((drone.battery.batteryDistance +((drone.time - drone.battery.dockedTime)*params["chargeRate"])), params["batteryDistance"])
                #update charging station to contain dropped off battery 
                swapIndex = action.node.batteriesHeld.index(action.batterySelected)
                action.node.batteriesHeld[swapIndex] = action.batteryDropped

                if (action.node.getCoords() == (0,0)) and (idx == 1): #stops 2 actions occuring at depot
                    del trip.actions[0]
                    action.prevAction = None
                if (action.node.getCoords() == (0,0)) and ("AtDepot" in str(type(action.nextAction))): #stops 2 actions occuring at depot
                    del trip.actions[-1]
                    action.nextAction = None 
                    break
                #print(f"switching battery")
            else:
                stationHistory = [] #clear station history when an action that isn't a change battery action is carried out
            #what the battery amount would be when arriving at the next node
            provisionalBatteryLevel = drone.battery.batteryDistance - distanceToTravel

            #if completing the next action will cause the drone to run out of battery
            if provisionalBatteryLevel < params["batteryChargeThreshold"]:
                unitX, unitY = Node.calculateUnitVector(action.node, action.nextAction.node)
                #this is how far the drone can get to the destination. It acts as the midpoint of the arc
                depletionCoordinate = (action.node.xCoord + int(unitX*drone.battery.batteryDistance)), (action.node.yCoord + int(unitY * drone.battery.batteryDistance))

                #filters the charging stations to only those that haven't been visited before, can be reached and are sensible to visit (in between the origin and destination)
                filters = [lambda x : x not in stationHistory, lambda x : x.inArc(angle = 90, circleCentre= action.node, midpoint = depletionCoordinate)]
                #apply filters
                feasibleChargingStations = list(filter(lambda x : all([f(x) for f in filters]), chargingStations))
                batteriesCopy = []
                
                #find the closest feasible charging station that has batteries 
                maxIters = len(feasibleChargingStations)
                iterations = 0
                while not batteriesCopy:
                    if iterations == maxIters:
                        break
                    chargingStation = max(feasibleChargingStations, key=lambda x : int(Node.distanceFinder(x, action.node)))
                    distanceToStation = Node.distanceFinder(action.node, chargingStation)
                    timeAtNextNode = drone.time + (distanceToStation / Parameters.droneSpeed) #next node will now be the charging station
                    batteriesCopy = copy.deepcopy(chargingStation.batteriesHeld)
                    #adding 20000/params["dronesSpeed"] means that batteries are not available unless they have a minimum charge in them 
                    batteriesCopy = list(filter(lambda x, timeAtNextNode = timeAtNextNode: x.dockedTime + (params["batteryChargeThreshold"]/params["droneSpeed"]) < timeAtNextNode if (x.dockedTime != None) else True, batteriesCopy))


                    if batteriesCopy: 
                        highestCharged = max([calculateChargedValues(battery, timeAtNextNode) for battery in batteriesCopy], key = lambda x : x.batteryDistance)
                        if highestCharged.batteryDistance > Parameters.batteryDistance:
                            highestCharged.batteryDistance = Parameters.batteryDistance
                        for battery in chargingStation.batteriesHeld:
                            if battery.id == highestCharged.id: 
                                realBattery = battery
                                realBattery.batteryDistance = highestCharged.batteryDistance #update this battery's charge value

                        
                        #this action will cause the drone to drop off it's depleted battery and pick up the one with highest charge
                        changeBatteryAction = ChangeBattery(chargingStation, drone.battery, realBattery)
                            #print("replacing at depot with charging node")


                        #print(trip)
                        trip.insertAction(idx+1, changeBatteryAction)
                        #print(trip)
                        isAddition = True
                    else: 
                        del feasibleChargingStations[feasibleChargingStations.index(chargingStation)]
                    iterations += 1

                #look for a feasible charging station that is not in the arc   
                filters =  [lambda x : x not in stationHistory, 
                lambda x : not x.inArc(angle = 90, circleCentre= action.node, midpoint = depletionCoordinate), 
                lambda x : Node.distanceFinder(x, action.node) < drone.battery.batteryDistance]    
                feasibleChargingStations = list(filter(lambda x : all([f(x) for f in filters]), chargingStations))
                
                maxIters = len(feasibleChargingStations)
                iterations = 0
                while not batteriesCopy:
                    if iterations == maxIters:
                        print("no charging station found")
                        return -1
                    chargingStation = min(feasibleChargingStations, key = lambda x : int(Node.distanceFinder(x, action.node)))

                    distanceToStation = Node.distanceFinder(action.node, chargingStation)
                    timeAtNextNode = drone.time + (distanceToStation / Parameters.droneSpeed)
                    batteriesCopy = copy.deepcopy(chargingStation.batteriesHeld)
                    batteriesCopy = list(filter(lambda x, timeAtNextNode = timeAtNextNode: x.dockedTime + (params["batteryChargeThreshold"]/params["droneSpeed"]) < timeAtNextNode if (x.dockedTime != None) else True, batteriesCopy))

                    if batteriesCopy:
                        highestCharged = max([calculateChargedValues(battery, timeAtNextNode) for battery in batteriesCopy], key = lambda x : x.batteryDistance)
                        if highestCharged.batteryDistance > Parameters.batteryDistance:
                            highestCharged.batteryDistance = Parameters.batteryDistance
                        for battery in chargingStation.batteriesHeld:
                            if battery.id == highestCharged.id: 
                                realBattery = battery
                                realBattery.batteryDistance = highestCharged.batteryDistance #update this battery's charge value

                        #this action will cause the drone to drop off it's depleted battery and pick up the one with highest charge
                        changeBatteryAction = ChangeBattery(chargingStation, drone.battery, realBattery)

                        trip.insertAction(idx+1, changeBatteryAction)
                        #print(trip)
                        isAddition = True
                    else: 
                        del feasibleChargingStations[feasibleChargingStations.index(chargingStation)]
                    iterations += 1
                stationHistory.append(chargingStation)
                #it is not possible for the drone to complete this trip
                if distanceToStation > drone.battery.batteryDistance:
                    print(f"station too far")
                    return -1
                drone.battery.batteryDistance -= distanceToStation
                
                #reduce list to only those batteries that exist at the station at the time the drone visits. 
                # print(batteriesCopy)
                # print(drone.time)
                # for battery12 in batteriesCopy: 
                #     print(battery12.dockedTime)
                #print(batteriesCopy)
                #check the list is not empty
             
                

            # if ("ChangeBattery" in str(type(action))) and ("AtDepot" in str(type(action.nextAction))):
            #     print(F"PROBLEM")
        
            else:
                drone.battery.batteryDistance = provisionalBatteryLevel
        drone.time = timeAtNextNode   
    return 2 
    #if there has been an addition to the trip start calculating again
    # if isAddition and run < 2:
    #     insertIntoTrip(trip, drone, run+1)


start()