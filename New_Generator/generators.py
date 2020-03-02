import random
import math
from generatorObjects.node import CustomerNode, ChargingNode, Node, DepletionPoint, Depot
import matplotlib.pyplot as plt
import parameters
from generatorObjects.drone import Drone 
from generatorObjects.action import Delivery, ChangeBattery, AtDepot
from generatorObjects.trip import Trip
from generatorObjects.package import Package 
import numpy as np
from sklearn.cluster import KMeans 
from scipy.spatial.distance import cdist
import tools

class Problem:
    """ 
    This class is used to generate random problems to the 
    Drone Delivery Problem 
    
    ...

    Attributes
    ----------
    nodes : List<Node> 
        a list of Node objects randomly generated
    
    maxRange: this is the highest value a node's coordinates 
    
    rangeMultiplyer : highest value added to maxRange

    noOfNodes : number of nodes to be randomly generated

    noOfPackages : number of packages to be randomly generated 

    nodemaxRangeRatio: value between 0 and 1 which is multiplied with rangeMultiplyer 
        to give a value which determines the spread distance of nodes. 

    distribution: setting for controlling the distribution of the nodes. 
        uniform = pseudo-randomly generated across the range 
        clustered = problem is randomly created with dense clusters of nodes 

    Methods 
    -------
    generateNodes()
        randomly generates the number of nodes specified by noOfNodes attribute

    
    """
    ax1 = parameters.ax
    
    def __init__(self, noOfNodes, noOfPackages, distribution="uniform" ):
        self.customers = []
        self.citySize = parameters.citySize 
        self.noOfNodes = noOfNodes
        self.noOfPackages = noOfPackages
        self.drones = []
        random.seed(parameters.seedVal)
        if not(distribution == "uniform" or distribution == "clustered"):
            print("distribution should be either 'uniform' or 'clustered' defaulting to uniform")
            distribution = "uniform"
        self.distribution = distribution

    def uniformGeneration(self):
        for _ in range(self.noOfNodes): 
            customer = CustomerNode()
            customer.random(0, self.citySize+1)
            self.customers.append(customer)
        
        

        for customer in self.customers:
            x, y = customer.getCoords()
            self.ax1.set_xlim([0,self.citySize])
            self.ax1.set_ylim([0,self.citySize])
            self.ax1.scatter(x,y, color='k')
        



    def createClusterCenters(self):
        numberOfClusters = math.floor(self.citySize * parameters.clusterToCitySizeRatio)
        clusterCenters = []
        for _ in range(numberOfClusters):
            cluster = CustomerNode() 
            cluster.random(0, self.citySize + 1)
            clusterCenters.append(cluster)
        return clusterCenters


    def clusteredGeneration(self):
        clusterCenters = self.createClusterCenters()
        for _ in range(self.noOfNodes): 
            customer = CustomerNode() #create customer node
            clusterIndex = random.randint(0, len(clusterCenters) - 1 ) #decide which cluster this node will belong 
            customer.randomWithinCircle(clusterCenters[clusterIndex], 1000)
            self.customers.append(customer)
        for customer in self.customers:
            x,y = customer.getCoords()
            self.ax1.set_xlim([0,self.citySize])
            self.ax1.set_ylim([0,self.citySize])
            self.ax1.scatter(x,y )
        


    def generateNodes(self):
        if self.distribution == "uniform":
            self.uniformGeneration()
        else:
            self.clusteredGeneration()

    def generateRechargingStations(self): #not used
        numberOfStations = math.floor(parameters.rechargingNodetoCitySizeRatio * parameters.citySize)

        for _ in range(numberOfStations): 
            chargingStation = ChargingNode()
            chargingStation.random(0, self.citySize)
            x,y = chargingStation.getCoords()
            self.ax1.scatter(x,y, color='b')


    def generateTripsandDrones(self):
        customersCopy = self.customers.copy() #no deep copy required
        currentDrone = Drone()
        packagePool = self.noOfPackages
        packageCounter = 0 #used for assigning ids to packages
        while packagePool > 0:  
            
            packagesInTrip = random.randint(1,min(parameters.droneCargoCapacity, packagePool)) #decide how many packages the drone will deliver, limited by cargo hold size
            packagePool -= packagesInTrip 

            tripActions = [] #contains the actions carried out in the trip 

            #creates package objects 
            for _ in range(packagesInTrip):
                packageCounter += 1
                pkg = Package(packageCounter)

                #randomly selects a customer node to deliver package 
                customer = self.customers[random.randrange(len(self.customers))] 
                
                #create drone action delivering package to customer 
                delivery = Delivery(customer, pkg)
                tripActions.append(delivery)
            deliveryActions = tripActions.copy()
            tripActions.insert(0, AtDepot())
            tripActions.append(AtDepot())

            orderedTripActions = tripActions[0] #depot
            orderedTrip = (self.nearestNeighbour([orderedTripActions], tripActions[1:]))

            trip = Trip(*orderedTrip) #creates trip object which forms the trip linked list 

            self.calculatePackageWeights(deliveryActions)

            tripDistance = Node.distanceCalc(*[action.node for action in trip.actions]) #pass in nodes visited in the trip to the trip distance calculator 
            if currentDrone.distanceLeft < tripDistance: 
                #drone is unable to take on this trip, create new drone 
                self.drones.append(currentDrone)
                currentDrone = Drone()
            else: 
                currentDrone.trips.append(trip)
                currentDrone.distanceLeft -= tripDistance
           
            #tools.drawTrip(trip)

        #add final drone to drone collection 
        if self.drones[-1] != currentDrone: 
            self.drones.append(currentDrone)


    '''
    Takes a trip and returns a trip with nodes ordered by nearest neighbour heuristic 
    '''
    def nearestNeighbour(self, orderedTrip, tripActions):
        consideredNode = orderedTrip[-1].node 
        distances = {}
        if len(tripActions) == 2: 
            orderedTrip.append(tripActions[-2])
            orderedTrip.append(tripActions[-1]) #append depot onto the end to finish the trip
            return orderedTrip

        for action in tripActions[:-1]: #don't include last node because that is depot 
           distances[action] = Node.distanceFinder(consideredNode, action.node)
        
        closest = min(distances.items(), key=lambda x : x[1])
        tripActions.remove(closest[0])

        orderedTrip.append(closest[0])

        return self.nearestNeighbour(orderedTrip, tripActions)
        
    def calculatePackageWeights(self,deliveries):
        maxWeight = parameters.droneWeightCapacity - (len(deliveries) -1)
        
        for delivery in deliveries: 
            packageWeight = random.randint(1,maxWeight)
            delivery.package.weight = packageWeight
            maxWeight -= packageWeight

            maxWeight += 1
    
    def calculateChargeDepletionPoints(self):
        #ax = plt.axes()
        
        depletionPoints = []
        for drone in self.drones:
            for trip in drone.trips:
                for action in trip.actions[1:]: 
                    distanceTraveled = Node.distanceFinder(action.node, action.prevAction.node)
                    drone.battery.batteryDistance -= distanceTraveled
                    if drone.battery.batteryDistance < 0: 
                        
                        depletionDistance  = distanceTraveled + drone.battery.batteryDistance
                        unitX, unitY = self.calculateUnitVector(action.prevAction.node, action.node) #ensure origin node is first arg and dest node is 2nd for correct unit vector direction

                        #tools.drawLine(action.prevAction.node, action.node, self.ax1)

                        originX, originY = action.prevAction.node.getCoords()
                        #self.ax1.plot(originX, originY, 'bo')

                        depletionX = int(originX + (unitX * depletionDistance))
                        depletionY = int(originY + (unitY * depletionDistance))

                        self.ax1.plot(depletionX, depletionY, 'ro')

                        depletionPoints.append(DepletionPoint(action = action, trip = trip, drone = drone, xCoord = depletionX, yCoord = depletionY))
                        drone.battery.batteryDistance = parameters.batteryDistance #reset battery charge to calculate next depletion point
        return depletionPoints
        #plt.show()

    def calculateUnitVector(self,node1, node2):
        x1, y1 = node1.getCoords() 
        x2, y2 = node2.getCoords()

        vectorX = x2 - x1 
        vectorY = y2 - y1

        magVector = math.sqrt(vectorX**2 + vectorY**2)

        unitX = vectorX/magVector
        unitY = vectorY/magVector

        return (unitX, unitY)

    def calculateRechargeStations(self, depletionPoints): 
        rechargeStations = []
        depletionCoords = [x.getCoords() for x in depletionPoints]
        clusterAmount = self.calculateNumberOfClusters(depletionCoords)

        depletionPointArray = np.array(depletionCoords).reshape(len(depletionCoords),2 )
        kmeans = KMeans(n_clusters = clusterAmount, random_state = parameters.seedVal).fit(depletionPointArray)

        for idx, vals in enumerate(kmeans.cluster_centers_):
            x,y = vals
            rechargeStations.append(ChargingNode(int(x),int(y)))
            self.ax1.plot(x,y,'yo')

        return rechargeStations

    def calculateNumberOfClusters(self, depletionCoordinates):
        pointArray = np.array(depletionCoordinates).reshape(len(depletionCoordinates),2)

        distortions = [] 
        numberOfClusters = 15 # max number of clusters possible
        print(numberOfClusters)
        print(len(pointArray))
        K = range(1,numberOfClusters)

        for k in K: 
            kmeanModel = KMeans(n_clusters = k).fit(pointArray)
            kmeanModel.fit(pointArray)
            distortions.append(sum(np.min(cdist(pointArray, kmeanModel.cluster_centers_, 'euclidean'), axis=1)) / pointArray.shape[0])
        #iterate through the distortion values and compare the the previous value (accessed through idx)
        #distortion is calculated as the sum of the squared distances from each point to its assigned center
        #the elbow is where distortion rate plateaus as more cluster centers get added
        for idx, val in enumerate(distortions[1:]):
            if val/distortions[idx] > .95:
                numberOfClusters = idx + 1 #select the number of clusters as the previous distortion value (+1 because python indexes from 0) 
                break #end loop when elbow is found 
       
        return numberOfClusters
    
    def includeChargingStations(self, depletionPoints, rechargingStations): 
        trip = depletionPoints[0].trip 
        numberOfRecharge = len(rechargingStations)
        newChargingStations = []
        for drone in self.drones: 
            if Node.distanceCalc(*[action.node for action in drone.getAllActions()]) > parameters.dayLength * parameters.droneSpeed:
                print("NEED TO CREATE A NEW BLOODY DRONE FFS1")

        for depletionPoint in depletionPoints: 
            action = depletionPoint.action
            trip = depletionPoint.trip
            drone = depletionPoint.drone
            
            if "AtDepot" in str(type(action.prevAction)): #if the depletion point was on the movement from the origin
                changeBatteryAction = ChangeBattery(action.prevAction.node, drone.battery) #create action to change battery at depot 
                Depot.batteriesHeld.append(drone.battery) #add the battery dropped off to the batteries held list
                Depot.capacity += 1 #increment the battery slot capacity required by depot
                drone.battery = changeBatteryAction.batterySelected #switch drone battery to the new battery which is selected when action is instantiated
                trip.actions[0] = changeBatteryAction #change first action from AtDepot to ChangeBattery

            else: 
                closestChargingPoint = min(rechargingStations, key = lambda x : Node.distanceFinder(x, action.prevAction.node))
                chargeRemaining = Node.distanceFinder(depletionPoint, action.prevAction.node) #charge at depletion point is 0 so charge remaining at start of action is distance from prevAction node to depletionPoint
                distanceToChargePoint = Node.distanceFinder(action.prevAction.node, closestChargingPoint)
                if distanceToChargePoint <= chargeRemaining: 
                    changeBatteryAction = ChangeBattery(closestChargingPoint, drone.battery) #create action to change battery at charging point
                    closestChargingPoint.batteriesHeld.append(drone.battery)
                    closestChargingPoint.capacity += 1
                    drone.battery = changeBatteryAction.batterySelected
                    idx = trip.actions.index(action)
                    trip.insertAction(idx, changeBatteryAction) #insert change battery action between origin and dest action nodes on linked list
                else: 
                    newStation = ChargingNode(depletionPoint.xCoord, depletionPoint.yCoord)
                    #self.ax1.plot(depletionPoint.xCoord, depletionPoint.yCoord, 'bx') #shows new stations added
                    changeBatteryAction = ChangeBattery(newStation, drone.battery)
                    newStation.batteriesHeld.append(drone.battery)
                    newStation.capacity += 1
                    drone.battery = changeBatteryAction.batterySelected
                    idx = trip.actions.index(action)
                    trip.insertAction(idx, changeBatteryAction)
                    #newChargingStations.append(newStation) #used for keeping track of the new stations
                    rechargingStations.append(newStation) #create a new charging station 
                    closestPoint = min(rechargingStations, key = lambda x : Node.distanceFinder(x, action.prevAction.node))
                    distance = Node.distanceFinder(action.prevAction.node, newStation)

        for drone in self.drones: 
            if Node.distanceCalc(*[action.node for action in drone.getAllActions()]) > parameters.dayLength * parameters.droneSpeed:
                print("NEED TO CREATE A NEW BLOODY DRONE FFS2")
        # print() 
        # print("capacity stats for kmean stations")
        # total = 0
        # for station in rechargingStations[:numberOfRecharge]:
        #     total += station.capacity
        #     print(station.capacity)
        # print(f"total for kmean stations is {total}")
        # total = 0
        # print("capacity for generated stations")
        # for station in newChargingStations: 
        #     total += station.capacity
        #     print(station.capacity)
        # print(f"total for new stations is {total}")
        # print()
        # print(f"batteries held in depot: {Depot.batteriesHeld} capacity: {Depot.capacity}")  