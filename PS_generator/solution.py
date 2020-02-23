import random
import parameters
import math
from drone import Drone 
from trip import Trip
from delivery import Delivery, ChangeBattery
from Node import Node
from problem import Problem


class Solution:
    def __init__(self, customers): 
        self.customers = customers #customers are represented by nodes 
        self.deliveries = [] #to be randomly allocated a delivery time and then distributed to trips
        self.drones = [] #trips are allocated to drones, a drone will have at least one trip 
        self.droneDeliveryAllocation = {} #dictionary containing temporary delivery assignment to drones (before trip construction)
        self.fitness = None
        self.values = [] #populated once generate has been called 
        random.seed(parameters.seed)

    def generate(self):
        numOfTrips = random.randint(1,parameters.customers) 
        numOfDrones = random.randint(1, min(numOfTrips, parameters.maxDrones))
    
        #create deliveries for each customer (node) 
        self.deliveries = [Delivery(x) for x in self.customers]
        #assign random delivery time to each delivery
        for delivery in self.deliveries: 
            delivery.time = random.randint(parameters.minimumDeliveryTime, parameters.dayLength)
        
        #ensure each drone has at least one delivery
        for idx in range (numOfDrones):
            self.droneDeliveryAllocation[idx] = [self.deliveries[idx]]
        
        #populate rest of delivery assignment dictionary 
        for idx in range(numOfDrones, len(self.deliveries)):
            droneAllocation = random.randrange(numOfDrones)
            self.droneDeliveryAllocation[droneAllocation].append(self.deliveries[idx])

        
        #create trips for each drone 
        for droneNo, assignedDeliveries in self.droneDeliveryAllocation.items():
            assignedDeliveries.sort(key=lambda x: x.time) #sort each drones deliveries so trips are in order
            
            #create trips within drone and add deliveries to trips
            trips = [] 
            while len(assignedDeliveries) > 0 :
                if parameters.droneCargoSlots > len(assignedDeliveries):
                    maxNumber = len(assignedDeliveries)
                else:
                    maxNumber = parameters.droneCargoSlots
                numberInTrip = random.randint(1,maxNumber) #randomly choose a number of packages to be in the trip, min = 1, max = cargoSize 
                trips.append(Trip(*assignedDeliveries[:numberInTrip]))
                del assignedDeliveries[:numberInTrip]
            self.drones.insert(droneNo, Drone(*trips))

        self.values = self.stringBuilder() #called last for problem file to be accurate 
    
    '''
    takes a list of all existing charging station nodes as well as a list of the deliveries that ran out of charge.
    changes the solution such that the trips include stops at the charging stations 
    '''
    def includeChargingStations(self, chargingStations, depletionPoints):
        #for each depletionPoint, find the nearest charging station 
        chargingStations.sort(key=lambda x: (x.xCoord, x.yCoord))
        print(f"charging stations are {chargingStations}")
        nodeidTripDictionary = self.getNodeIdTripDictionary()
        for depletionPoint in depletionPoints: 
            delivery = depletionPoint.delivery

            #check if this is the first delivery in a trip
            #if it is, switch battery at depot
            if delivery.prevDelivery == None: 
                trip = nodeidTripDictionary[delivery.node.id]
                #calculate time drone will be at the depot based on where it delivers the first package in the trip 
                time = delivery.time - (Node.distanceCalc(Problem.depotCharging, delivery.node) // parameters.droneSpeed)
                #create ChangeBattery action for depot node
                switchBatteryAction = ChangeBattery(node = Problem.depotCharging, prevDelivery = None, nextDelivery = delivery, time = time)
                
                delivery.prevDelivery = switchBatteryAction
                trip.deliveries.insert(0, switchBatteryAction)
            

        #print(f"closest charging station to {testPoint} is {Node.binarySearch(chargingStations, 0, len(chargingStations)-1, testPoint)}")

    
    '''
    Returns a dictionary of delivery node id -> trip. 
    List is sorted on the node ids of the delivery destinations 
    '''
    def getNodeIdTripDictionary(self):
        #create dictionary of all deliveries and their respective trips 
        return {delivery.node.id : trip for drone in self.drones for trip in drone.trips for delivery in trip.deliveries}



    def stringBuilder(self): 
        outputElements = []
        for drone in self.drones: 
            outputElements.append(len(drone.trips))
            for trip in drone.trips:
                outputElements.append(len(trip.deliveries))
                for delivery in trip.deliveries:
                    outputElements.append(delivery.node.id)
                    outputElements.append(delivery.time)
        return ",".join([str(x) for x in outputElements])

    def writeToFile(self):
        with open("solution.txt", "w") as file:
            file.seek(0)
            file.write(self.values)

    def getAllDeliveries(self): 
        deliveries = [delivery for drone in self.drones for trip in drone.trips for delivery in trip.deliveries]        
        return deliveries
    
    def getAllTrips(self):
        trips = [trip for drone in self.drones for trip in drone.trips]
        return trips

    def getAllNodes(self):
        nodes = [delivery.node for drone in self.drones for trip in drone.trips for delivery in trip.deliveries]
        return nodes

    #probably needs to be re-written 
    #take into account the distance from the depot to the first delivery and the distance from the last delivery to the depot
    def evaluate(self, problem): #takes in a string which represents a problem vector as argument
        solutionVals = repr(self).split(",")
        problemVals = str(problem).split(", ") #str conversion not needed if argument is string
        solutionScore = 0 #the fitness score for the solution
        offset = 2 #nodes start at position 2 in the string 
        tripCountIdx = 0 #index for referencing the solution string
        finished = False
        while not finished:
            if tripCountIdx < len(solutionVals):
                deliveriesForDrone = 0
                tripsForDrone = 0
                droneTrips = int(solutionVals[tripCountIdx]) #how many trips the first drone has
                tripCountIdx += 1
         

                while droneTrips > 0:
                    tripsForDrone += 1
                    #print(f"count index is {tripCountIdx}, droneTrips is {droneTrips}")
                    deliveryCount = int(solutionVals[tripCountIdx]) #how many deliveries are in the first trip
                    #print(deliveryCount)

                    nodes = []
                    nodes.append(Node(xCoord = 0, yCoord = 0)) #insert depot node into list as every trip will start and end here

                    #iterates through each delivery in a trip
                    for idx in range(tripCountIdx + 2, tripCountIdx + (deliveryCount * 2) + 1, 2):
                        #determine if the delivery is late, only check if delivery is late as if it is early then the drone is allowed to wait 
                        timeDelivered = solutionVals[idx] 
                        nodeID = int(solutionVals[idx -1])
                        problemNodeIdx = (nodeID * 4) + 2 #indexes the start of the node in the problem vector 
                        if timeDelivered > problemVals[problemNodeIdx + 3]: #late delivery penalty is 1000 
                            solutionScore += 1000
                        xCoord = problemVals[problemNodeIdx]
                        yCoord = problemVals[problemNodeIdx + 1]
                        #print(f"x = {xCoord}, y = {yCoord}")
                        nodes.append(Node(xCoord = int(xCoord), yCoord = int(yCoord)))
                        #print(nodes)

                       # print(f"time delivered is {solutionVals[idx]} to node {solutionVals[idx -1]}")
                    nodes.append(Node(xCoord = 0, yCoord = 0)) #insert depot node into list marking the return journey back to depot at end of trip
                    solutionScore += Node.distanceCalc(*nodes)
                    tripCountIdx += (deliveryCount * 2) + 1
                    
                    droneTrips -= 1
                
            else:
                finished = True
                continue
        self.fitness = solutionScore
    
    def __repr__(self):
        return str(self.values)


    def __str__(self):
        return self.values 