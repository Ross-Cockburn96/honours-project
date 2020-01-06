import random
import parameters
from Node import Node
class Problem: 
    def __init__(self, solution): 
        self.solution = solution 
    
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
        

    def generate(self):
        allTrips = self.solution.getAllTrips() #get list of all trips that are in the solution 
        for trip in allTrips: 
            self.nodeTimeSlotCalc(trip)
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
            
                
