import random
import math
import parameters
from Node import Node, RechargeNode, DepletionPoint
import tools
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from sklearn.cluster import KMeans 
from scipy.spatial.distance import cdist
class Problem: 
    depot = Node(xCoord = 0, yCoord = 0)
    #depot and depot charging are the same node, however in order to distinguish between a drone returning to depot to get more packages and a drone that is getting more packages and exchanging batteries, the node is duplicated with different ids and duplicated in problem file 
    depotCharging = (RechargeNode(parameters.customers+1, xCoord= 0, yCoord=0))
    def __init__(self, solution): 
        random.seed(parameters.seed)
        self.values = [] #only populated after 'generate' function has been called
        self.rechargeStations = [] #populated after 'generate' function has been called 
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
        #TODO:
        #FIRST DELIVERY IN TRIP NEEDS TO CONSIDER WHAT TIME THE PREVIOUS TRIP WAS COMPLETED 
        colourForTrip = (random.uniform(0,1), random.uniform(0,1), random.uniform(0,1))
        #print(f"considering trip {trip}")
        prevNode = self.depot
        prevDelivery = None
        print(f"start time in coord calc is {trip.startTime}")
        maxTravelDistance = (trip.deliveries[0].time - trip.startTime) * parameters.droneSpeed
        oldIs = trip.deliveries[0].time * parameters.droneSpeed
        print(f"max Travel distance is {maxTravelDistance}, time is {trip.deliveries[0].time}, old time is {oldIs}")
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
        prevTrip = None 
        startTime = 0 

        for idx, drone in enumerate(self.solution.drones):
            print(f"drone {idx}")
            prevTrip = None
            startTime = 0
            for idx2, trip in enumerate(drone.trips):
                print(f"trip {idx2}, prevTrip = {prevTrip}")
                self.nodeTimeSlotCalc(trip)
                
                #doesn't work node corrd calc needs times and times need coords
                if prevTrip != None: 
                    print(f"prevTrip start time is {prevTrip.startTime}")
                    startTime = prevTrip.deliveries[-1].time + (Node.distanceCalc(self.depot, prevTrip.deliveries[-1].node) // parameters.droneSpeed)
                    trip.startTime = startTime
                else:
                    trip.startTime = startTime
                    
                self.nodeCoordCalc(trip, ax)
                print()
                numOfDeliveries = len(trip.deliveries)
                maxWeight = parameters.droneCapacity - (numOfDeliveries -1) #ensure that the max weight is set such that all packages have at least a weight of 1 
                for delivery in trip.deliveries:
                    packageWeight = random.randint(1, maxWeight)
                    maxWeight -= packageWeight
                    delivery.weight = packageWeight
                    maxWeight += 1 #once a package is assigned a weight increase the max weight by 1 since there is one less package left to assign 
                prevTrip = trip







        # for trip in allTrips: 
        #     self.nodeTimeSlotCalc(trip)
        #     self.nodeCoordCalc(trip, ax)
        #     if prevTrip != None: 
        #         startTime = prevTrip.deliveries[-1].time + (Node.distanceCalc(self.depot, prevTrip.deliveries[-1].node) // parameters.droneSpeed)
            
            
        tools.drawTrip(max(allTrips, key=lambda x : len(x.deliveries))) #draws the largest trip in the problem 
        
        depletionPoints, ax = self.calculateDepletionPoints()
        depletionCoordinates = [x.getCoords() for x in depletionPoints]
        #carry out k-means clustering 
        clusterAmount = self.calculateNumberOfClusters(depletionCoordinates)
        depletionPointArray = np.array(depletionCoordinates).reshape(len(depletionCoordinates), 2)
        kmeans = KMeans(n_clusters = clusterAmount, random_state = 0).fit(depletionPointArray)
        #print(f"clusters are at {kmeans.cluster_centers_}, cluster amount was {clusterAmount}")
        for idx, vals in enumerate(kmeans.cluster_centers_):
            x,y = vals
            self.rechargeStations.append(RechargeNode(idx+ (parameters.customers + 2), int(x),int(y)))
            ax.plot(x,y,'yo')
        plt.show()
        self.solution.includeChargingStations(self.rechargeStations, depletionPoints)
        print("Drawing Drone Trips")
        tools.drawDroneTrips(self.solution.drones[0])
        self.values = self.stringBuilder()
    '''
    Based on the current problem and solution, tests to see where nodes are running out of battery. 
    Uses the Node data structure for representing depletion points. returns depletion points, which are tuples 
    '''
    def calculateDepletionPoints(self):
        ax = plt.axes()
        ax.add_patch(patches.Rectangle((0,0), parameters.citySizeMax, parameters.citySizeMax))
        depletionPoints = [] #this is a list of coordinates where drones have ran out of charge, list of tuples
        #find where drones run out of charge
        for drone in self.solution.drones: 
            for delivery in drone.getAllDeliveries():
                if delivery.prevDelivery != None:  #if the delivery is not first in a trip
                    drone.charge -= (delivery.time - delivery.prevDelivery.time)
                    if drone.charge < 0:
                        distanceTraveled = ((delivery.time - delivery.prevDelivery.time) + drone.charge) * parameters.droneSpeed #plus because charge is negative 

                        unitX, unitY = self.calculateUnitVector(delivery.prevDelivery.node, delivery.node)
                        
                        tools.drawLine(delivery.prevDelivery.node, delivery.node, ax)

                        originX, originY = delivery.prevDelivery.node.getCoords() 
                        
                        if originX + (unitX * distanceTraveled) in range(originX, delivery.node.xCoord + 1):
                            plotX = originX + (unitX * distanceTraveled)
                        else: 
                            plotX = delivery.node.xCoord
                        
                        if originY + (unitY * distanceTraveled) in range(originY, delivery.node.yCoord+1):
                            plotY = originY + (unitY * distanceTraveled)
                        else:
                            plotY = delivery.node.yCoord

                        ax.plot(plotX, plotY, 'ro')
                        depletionPoints.append(DepletionPoint(delivery, xCoord = plotX, yCoord = plotY)) 
                        drone.charge = parameters.batteryCharge #reset charge 
                else: #if the delivery is first in a trip 
                    drone.charge -= delivery.time
                    if drone.charge < 0: 
                        distanceTraveled = (delivery.time + drone.charge) * parameters.droneSpeed
                        
                        unitX, unitY = self.calculateUnitVector(self.depot, delivery.node)

                        tools.drawLine(self.depot, delivery.node, ax)

                        originX, originY = self.depot.getCoords()  # 0,0
                        
                        if originX + (unitX * distanceTraveled) in range(originX, delivery.node.xCoord + 1):
                            plotX = originX + (unitX * distanceTraveled)
                        else: 
                            plotX = delivery.node.xCoord
                        
                        if originY + (unitY * distanceTraveled) in range(originY, delivery.node.yCoord+1):
                            plotY = originY + (unitY * distanceTraveled)
                        else:
                            plotY = delivery.node.yCoord

                        ax.plot(plotX, plotY, 'ro')
                        depletionPoints.append(DepletionPoint(delivery, xCoord = plotX, yCoord = plotY))
                        drone.charge = parameters.batteryCharge
        return depletionPoints, ax

    #uses elbow method to calculate the optimal number of clusters
    def calculateNumberOfClusters(self, points):
        pointArray = np.array(points).reshape(len(points), 2)
        
        distortions = [] 
        K = range(1,10) #

        for k in K:
            kmeanModel = KMeans(n_clusters=k).fit(pointArray)
            kmeanModel.fit(pointArray)
            distortions.append(sum(np.min(cdist(pointArray, kmeanModel.cluster_centers_, 'euclidean'), axis=1)) / pointArray.shape[0])
        
        numberOfClusters = 10 #maximum number of clusters possible 

        #iterate through the distortion values and compare the the previous value (accessed through idx)
        #distortion is calculated as the sum of the squared distances from each point to its assigned center
        #the elbow is where distortion rate plateaus as more cluster centers get added
        for idx, val in enumerate(distortions[1:]): 
            if val/distortions[idx] > .85: 
                numberOfClusters = idx + 1 #select the number of clusters as the previous distortion values index (+1 because python indexes from 0)
                break #end loop when elbow is found 
        # plt.clf()
        # plt.plot(K, distortions, 'bx-')
        # plt.xlabel('k')
        # plt.ylabel('Distortion')
        # plt.title('The Elbow Method showing the optimal k')
        # plt.show()
        return numberOfClusters

    def calculateUnitVector(self,node1, node2):
        x1, y1 = node1.getCoords() 
        x2, y2 = node2.getCoords()

        vectorX = x2 - x1 
        vectorY = y2 - y1

        magVector = math.sqrt(vectorX**2 + vectorY**2)

        unitX = vectorX/magVector
        unitY = vectorY/magVector

        return (unitX, unitY)

    #outputs a string representation of the problem 
    def stringBuilder(self):
        outputElements = [] 
        deliveries = self.solution.getAllDeliveries()
        outputElements.append(len(deliveries)) #number of nodes
        outputElements.append(len(self.rechargeStations))
        outputElements.append(len(deliveries)) #number of packages

        outputElements.append(Node(0, 0, 0)) #insert depot node at 0,0 coordinates 
        nodes = self.solution.getAllNodes() 
        nodes.sort(key=lambda x: x.id) #sorts nodes in order of id 
        outputElements.extend(nodes) #adds nodes to problem string 
        
        #add depot recharge node 
        outputElements.append(str(self.depotCharging))
        #add recharge stations to problem string 
        for station in self.rechargeStations:
            outputElements.append(str(station))

        #adds package details to problem string     
        for delivery in deliveries: 
            if delivery.node.id < parameters.customers+ 1: #only deliveries with these nodes will be package deliveries 
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
        
            
                
