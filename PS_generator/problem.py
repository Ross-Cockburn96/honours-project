import random
import parameters
from Node import Node
class Problem: 
    def __init__(self, solution): 
        self.solution = solution 
    
    #time slots are calculated for each customer based on the time that the solution says the delivery arrived. This ensures time slots are feasible. 
    def nodeTimeSlotCalc(self, trip):
        for delivery in trip.deliveries: 
            if delivery.time - 100 < 0 : 
                delivery.node.openTime = 0
            else: 
                delivery.node.openTime = delivery.time - 100
            if delivery.time + 100 > parameters.dayLength:
                delivery.node.closeTime = parameters.dayLength
            else:
                delivery.node.closeTime = delivery.time + 100
    
    #coordinates are constrained by the distance a node can travel in the time until the next delivery occurs. A drone can wait if it is early. 
    def nodeCoordCalc(self, trip):
        prevDelivery = trip.deliveries[0]
        prevNode = prevDelivery.node
        prevNode.random(0, parameters.citySizeMax)
        restOfTrip = trip.deliveries[1:]

        print(prevDelivery)
        for delivery in restOfTrip:
            timeSlotDifference = delivery.time - prevDelivery.time
            maxTravelDistance = (timeSlotDifference * parameters.droneSpeed)/1000
            delivery.node.randomValidCoord(prevNode, maxTravelDistance)
            prevNode = delivery.node
            print(delivery)
        
        print("")

    def generate(self):
        allTrips = self.solution.getAllTrips() #get list of all trips that are in the solution 
        for trip in allTrips: 
            self.nodeTimeSlotCalc(trip)
            self.nodeCoordCalc(trip)
            numOfDeliveries = len(trip.deliveries)
            maxWeight = parameters.droneCapacity - (numOfDeliveries -1) #ensure that the max weight is set such that all packages have at least a weight of 1 
            for delivery in trip.deliveries:
                packageWeight = random.randint(1, maxWeight)
                maxWeight -= packageWeight
                delivery.weight = packageWeight
                maxWeight += 1 #once a package is assigned a weight increase the max weight by 1 since there is one less package left to assign 

    
    def __str__(self):
        outputElements = [] 
        deliveries = self.solution.getAllDeliveries()
        outputElements.append(len(deliveries)) #number of nodes
        outputElements.append(len(deliveries)) #number of packages
       
        for delivery in deliveries: 
            outputElements.append(str(delivery.node))

        for delivery in deliveries: 
            outputElements.append(delivery.node.id)
            outputElements.append(delivery.weight)
        return ", ".join([str(x) for x in outputElements])
            
                
