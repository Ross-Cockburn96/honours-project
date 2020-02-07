import random
import math
import parameters
from Node import Node
import tools
import matplotlib.pyplot as plt
class Problem: 
    depot = Node(xCoord = 0, yCoord = 0)
    def __init__(self, solution): 
        random.seed(parameters.seed)
        self.values = [] #only populated after 'generate' function has been called
        self.solution = solution 
    
    #time slots are calculated for each customer based on the time that the solution says the delivery arrived. This ensures time slots are feasible. 
    def nodeTimeSlotCalc(self, trip):
        for delivery in trip.deliveries: 
            
            #drawing a uniform random variable as mean widens the crest of the normal curve to the bounds of the range
            mean = random.randint(0,parameters.dayLength/4) 
            #print(f"mean is {mean}")
            #halfRange means the open time will be solution delivery time - halfRange and close time will be solution delivery time + halfRange, giving the full range
            halfRange = parameters.minimumDeliveryTime + abs(math.floor(random.gauss(mean, parameters.timeSlotStandardDev)))
            #print(f"half range is {halfRange}, minimum delivery time is {parameters.minimumDeliveryTime}")
            if delivery.time - halfRange < 0 : 
                delivery.node.openTime = 0
            else: 
                delivery.node.openTime = delivery.time - halfRange
            if delivery.time + halfRange > parameters.dayLength:
                delivery.node.closeTime = parameters.dayLength
            else:
                delivery.node.closeTime = delivery.time + halfRange
            #print(f"open time is {delivery.node.openTime}, solution delivery is {delivery.time}, close time is {delivery.node.closeTime}")
    
    #coordinates are constrained by the distance a node can travel in the time until the next delivery occurs. A drone can wait if it is early. 
    def nodeCoordCalc(self, trip, ax):
        colourForTrip = (random.uniform(0,1), random.uniform(0,1), random.uniform(0,1))
        #print(f"considering trip {trip}")
        prevNode = self.depot
        prevDelivery = None
        maxTravelDistance = trip.deliveries[0].time * parameters.droneSpeed
        #tools.drawCircle(self.depot, maxTravelDistance,ax, colourForTrip)
        for delivery in trip.deliveries:
            if prevDelivery != None:
                timeSlotDifference = delivery.time - prevDelivery.time
                maxTravelDistance = (timeSlotDifference * parameters.droneSpeed)
            delivery.node.randomValidCoord(prevNode, maxTravelDistance)
            #tools.drawCircle(delivery.node, maxTravelDistance, ax, colourForTrip)
            #tools.drawLine(prevNode, delivery.node, ax, colourForTrip)
            prevDelivery = delivery
            prevNode = prevDelivery.node

    def generate(self):
        # fig = plt.figure()
        # ax = fig.add_subplot(111)
        # ax.set_ylim(-50,parameters.citySizeMax)
        # ax.set_xlim(-50,parameters.citySizeMax)
        ax= 1
        allTrips = self.solution.getAllTrips() #get list of all trips that are in the solution 
        
        for trip in allTrips: 
            self.nodeTimeSlotCalc(trip)
            self.nodeCoordCalc(trip, ax)
            numOfDeliveries = len(trip.deliveries)
            maxWeight = parameters.droneCapacity - (numOfDeliveries -1) #ensure that the max weight is set such that all packages have at least a weight of 1 
            for delivery in trip.deliveries:
                packageWeight = random.randint(1, maxWeight)
                maxWeight -= packageWeight
                delivery.weight = packageWeight
                maxWeight += 1 #once a package is assigned a weight increase the max weight by 1 since there is one less package left to assign 
        self.values = self.stringBuilder()
        tools.drawTrip(max(allTrips, key=lambda x : len(x.deliveries))) #draws the largest trip in the problem 
        
        #find where drones run out of charge

        # for drone in self.solution.drones: 
        #     for delivery in drone.getAllDeliveries():


        
        #plt.show()
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

    def writeToFile(self): 
        with open("problem.txt", "w") as file: 
            file.seek(0)
            file.write(self.values)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.values
        
            
                
