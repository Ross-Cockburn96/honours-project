import random
import parameters
from Node import Node
class Problem: 
    def __init__(self, solution): 
        self.values = [] #only populated after 'generate' function has been called
        self.solution = solution 
    
    #time slots are calculated for each customer based on the time that the solution says the delivery arrived. This ensures time slots are feasible. 
    def nodeTimeSlotCalc(self, trip):
        for delivery in trip.deliveries: 
            if delivery.time - parameters.minimumDeliveryTime < 0 : 
                delivery.node.openTime = 0
            else: 
                delivery.node.openTime = delivery.time - parameters.minimumDeliveryTime
            if delivery.time + parameters.minimumDeliveryTime > parameters.dayLength:
                delivery.node.closeTime = parameters.dayLength
            else:
                delivery.node.closeTime = delivery.time + parameters.minimumDeliveryTime
    
    #coordinates are constrained by the distance a node can travel in the time until the next delivery occurs. A drone can wait if it is early. 
    def nodeCoordCalc(self, trip):
        prevDelivery = trip.deliveries[0]
        prevNode = prevDelivery.node
        prevNode.random(0, parameters.citySizeMax)
        restOfTrip = trip.deliveries[1:]

        for delivery in restOfTrip:
            timeSlotDifference = delivery.time - prevDelivery.time
            maxTravelDistance = (timeSlotDifference * parameters.droneSpeed)
            delivery.node.randomValidCoord(prevNode, maxTravelDistance)
            prevDelivery = delivery
            prevNode = prevDelivery.node
        
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
        self.values = self.stringBuilder()
    
    #outputs a string representation of the problem 
    def stringBuilder(self):
        outputElements = [] 
        deliveries = self.solution.getAllDeliveries()
        outputElements.append(len(deliveries)) #number of nodes
        outputElements.append(len(deliveries)) #number of packages

        outputElements.append(Node(0, 0, 0)) #insert depot node at 0,0 coordinates 
        nodes = self.solution.getAllNodes() 
        nodes.sort(key=lambda x: x.id) #sorts nodes in order of id 
        outputElements.extend(nodes)
        
            
        for delivery in deliveries: 
            outputElements.append(delivery.node.id)
            outputElements.append(delivery.weight)
        return ", ".join([str(x) for x in outputElements])

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.values
        
            
                
