import random
import math
import os 
import copy
from generatorObjects.node import CustomerNode, ChargingNode, Node, DepletionPoint, Depot
import matplotlib.pyplot as plt
from .parameters import Parameters 
from generatorObjects.drone import Drone 
from generatorObjects.action import Delivery, ChangeBattery, AtDepot
from generatorObjects.trip import Trip
from generatorObjects.package import Package 
from generatorObjects.battery import Battery
import numpy as np
from sklearn.cluster import KMeans 
from scipy.spatial.distance import cdist
import new_generator.tools

class Generator:
    ax1 = Parameters.ax
    
    def __init__(self, distribution="uniform" ):
        self.customers = []
        self.citySize = Parameters.citySize 
        self.noOfNodes = Parameters.noOfCustomers
        self.noOfPackages = Parameters.noOfPackages
        self.drones = []
        self.rechargeStations = []
        self.packages = []
        random.seed(Parameters.seedVal)

        if not(distribution == "uniform" or distribution == "clustered"):
            print("distribution should be either 'uniform' or 'clustered' defaulting to uniform")
            distribution = "uniform"
        self.distribution = distribution

    def uniformGeneration(self):
        for _ in range(self.noOfNodes): 
            customer = CustomerNode.createNew()
            customer.random(0, self.citySize+1)
            self.customers.append(customer)
        
        

        for customer in self.customers:
            x, y = customer.getCoords()
            self.ax1.set_xlim([0,self.citySize])
            self.ax1.set_ylim([0,self.citySize])
            #self.ax1.scatter(x,y, color='k')
        



    def createClusterCenters(self):
        numberOfClusters = math.floor(self.citySize * Parameters.clusterToCitySizeRatio)
        clusterCenters = []
        for _ in range(numberOfClusters):
            cluster = CustomerNode.createNew() 
            cluster.random(0, self.citySize + 1)
            clusterCenters.append(cluster)
        return clusterCenters


    def clusteredGeneration(self):
        clusterCenters = self.createClusterCenters()
        for _ in range(self.noOfNodes): 
            customer = CustomerNode.createNew() #create customer node
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
        numberOfStations = math.floor(Parameters.rechargingNodetoCitySizeRatio * Parameters.citySize)

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
            
            packagesInTrip = random.randint(1,min(Parameters.droneCargoCapacity, packagePool)) #decide how many packages the drone will deliver, limited by cargo hold size
            packagePool -= packagesInTrip 

            tripActions = [] #contains the actions carried out in the trip 

            #creates package objects 
            for _ in range(packagesInTrip):
                packageCounter += 1
                pkg = Package(packageCounter)
                self.packages.append(pkg)

                #randomly selects a customer node to deliver package 
                customer = self.customers[random.randrange(len(self.customers))] 
                pkg.destination = customer
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
                currentDrone = Drone(trip)
                currentDrone.distanceLeft -= tripDistance
            else: 
                currentDrone.trips.append(trip)
                currentDrone.distanceLeft -= tripDistance
           
        if len(self.drones) == 0 : 
            self.drones.append(currentDrone)
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
        maxWeight = Parameters.droneWeightCapacity - (len(deliveries) -1)
        
        for delivery in deliveries: 
            packageWeight = random.randint(1,maxWeight)
            delivery.package.weight = packageWeight
            maxWeight -= packageWeight

            maxWeight += 1
    
    def calculateChargeDepletionPoints(self):
        #ax = plt.axes()
        depletionPoints = []
        for drone in self.drones:
            drone.reset() #ensure drones all have initial state before calculations, reset does not change the drone trips 
            for trip in drone.trips:        
                for action in trip.actions[:-1]: 
                    distanceTraveled = round(Node.distanceFinder(action.node, action.nextAction.node))
                    if "Delivery" in str(type(action)) or "AtDepot" in str(type(action)):
                        drone.battery.batteryDistance -= distanceTraveled
                        if drone.battery.batteryDistance == -1: #account for rounding error 
                            drone.battery.batteryDistance = 0
                    else: #ChangeBattery action 
                        drone.battery = action.batterySelected
                        drone.battery.batteryDistance = Parameters.batteryDistance #replenishing charge instead of physically changing battery to make life easier as it doesn't matter for calculations
                        drone.battery.batteryDistance -= distanceTraveled
                    if drone.battery.batteryDistance < 0: 
                        depletionDistance  = distanceTraveled + drone.battery.batteryDistance
                        unitX, unitY = self.calculateUnitVector(action.node, action.nextAction.node) #ensure origin node is first arg and dest node is 2nd for correct unit vector direction

                        #tools.drawLine(action.node, action.node, self.ax1)

                        originX, originY = action.node.getCoords()
                        #self.ax1.plot(originX, originY, 'bo')
                        adjustedDistance = max(depletionDistance - 100, 0) #there was a bug when depletion points were created too close to the exact position the battery was depleted
                        depletionX = int(originX + (unitX * adjustedDistance))
                        depletionY = int(originY + (unitY * adjustedDistance))
                        #self.ax1.plot(depletionX, depletionY, 'ro')
                        depletionPoints.append(DepletionPoint(action = action.nextAction, trip = trip, drone = drone, batteryUsed = copy.copy(drone.battery),xCoord = depletionX, yCoord = depletionY))
                        drone.battery.batteryDistance = Parameters.batteryDistance #reset battery charge to calculate next depletion point
        #plt.show()]
        return depletionPoints
        

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
        seed = random.randint(1,10)
        kmeans = KMeans(n_clusters = clusterAmount, random_state = seed).fit(depletionPointArray)
        print(kmeans.cluster_centers_)
        for idx, vals in enumerate(kmeans.cluster_centers_):
            x,y = vals
            rechargeStations.append(ChargingNode(int(x),int(y)))
            self.ax1.plot(x,y,'yo')

        return rechargeStations

    def calculateNumberOfClusters(self, depletionCoordinates):
        pointArray = np.array(depletionCoordinates).reshape(len(depletionCoordinates),2)

        distortions = [] 
        
        numberOfClusters = 15 # max number of clusters possible
        if len(depletionCoordinates) < numberOfClusters: 
            numberOfClusters = len(depletionCoordinates)
        K = range(1,numberOfClusters)
        
        seed = random.randint(1,10)
        for k in K: 
            kmeanModel = KMeans(n_clusters = k, random_state = seed).fit(pointArray)
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


    def includeNewChargingStations(self, depletionPoints, rechargingStations):
        for idx, depletionPoint in enumerate(depletionPoints): 
            action = depletionPoint.action
            trip = depletionPoint.trip
            drone = depletionPoint.drone

            if depletionPoint.batteryUsed.id > drone.battery.id:
                drone.battery = depletionPoint.batteryUsed
            
            changeBatteryAction = ChangeBattery(rechargingStations[idx], drone.battery)
            drone.battery = changeBatteryAction.batterySelected
            self.rechargeStations.append(rechargingStations[idx])
            rechargingStations[idx].batteriesHeld.append(drone.battery)
            idx = trip.actions.index(action)
            trip.insertAction(idx, changeBatteryAction)

    def includeChargingStations(self, depletionPoints, rechargingStations): 
        trip = depletionPoints[0].trip 
        numberOfRecharge = len(rechargingStations)
        newChargingStations = []
        chargingDepot = Depot()
        chargingDepot.id = len(self.customers)+1
        originalState_batteries = []
        newActions = []
        numberOfDronesAtStart = len(self.drones)
        for drone in self.drones:
            originalState_batteries.append(drone.battery)
        for depletionPoint in depletionPoints: 
            #print(f"considering depletion point {depletionPoint.getCoords()}")
            action = depletionPoint.action
            #print(F"prev action is {action.prevAction.node}, current action is {action.node}")
            trip = depletionPoint.trip
            drone = depletionPoint.drone
            if depletionPoint.batteryUsed.id > drone.battery.id:
                drone.battery = depletionPoint.batteryUsed
            
            if "AtDepot" in str(type(action.prevAction)): #if the depletion point was on the movement from the origin
                changeBatteryAction = ChangeBattery(chargingDepot, drone.battery) #create action to change battery at depot. Change battery automatically switches the drone's battery to a new one
                drone.battery = changeBatteryAction.batterySelected #switch drone battery to the new battery which is selected when action is instantiated
                newActions.append(changeBatteryAction)
                Depot.batteriesHeld.append(drone.battery) #add the battery dropped off to the batteries held list 
                Depot.capacity += 1 #increment the battery slot capacity required by depot
                del trip.actions[0]
                trip.insertAction(0, changeBatteryAction)  #change first action from AtDepot to ChangeBattery
                
                
            else: 
                closestChargingPoint = min(rechargingStations, key = lambda x : int(Node.distanceFinder(x, action.prevAction.node)))
                #print(f"closest charging Point is {closestChargingPoint.getCoords()}")
                chargeRemaining = int(Node.distanceFinder(depletionPoint, action.prevAction.node)) #charge at depletion point is 0 so charge remaining at start of action is distance from prevAction node to depletionPoint
                distanceToChargePoint = int(Node.distanceFinder(action.prevAction.node, closestChargingPoint))
                if distanceToChargePoint <= chargeRemaining: 
                    changeBatteryAction = ChangeBattery(closestChargingPoint, drone.battery) #create action to change battery at charging point
                    drone.battery = changeBatteryAction.batterySelected
                    newActions.append(changeBatteryAction)
                    closestChargingPoint.batteriesHeld.append(drone.battery)
                    closestChargingPoint.capacity += 1
                    idx = trip.actions.index(action)
                    trip.insertAction(idx, changeBatteryAction) #insert change battery action between origin and dest action nodes on linked list
                else: 
                    newStation = ChargingNode(depletionPoint.xCoord, depletionPoint.yCoord)
                    #self.ax1.plot(depletionPoint.xCoord, depletionPoint.yCoord, 'bx') #shows new stations added
                    changeBatteryAction = ChangeBattery(newStation, drone.battery)
                    drone.battery = changeBatteryAction.batterySelected
                    newActions.append(changeBatteryAction)
                    newStation.batteriesHeld.append(drone.battery)
                    newStation.capacity += 1
                    idx = trip.actions.index(action)
                    trip.insertAction(idx, changeBatteryAction)
                    #newChargingStations.append(newStation) #used for keeping track of the new stations
                    rechargingStations.append(newStation) #create a new charging station 
                    closestPoint = min(rechargingStations, key = lambda x : Node.distanceFinder(x, action.prevAction.node))
                    distance = Node.distanceFinder(action.prevAction.node, newStation)

        
        #check that each drone can complete its trips within a day, if it can't move trip to drone with space (can only be last in list) or create a new drone 
        for drone in self.drones: 
            if Node.distanceCalc(*[action.node for action in drone.getAllActions()]) > Parameters.dayLength * Parameters.droneSpeed:
                lastTrip = drone.trips.pop() #remove trip from drone
                tripDistance =  Node.distanceCalc(*[action.node for action in lastTrip.actions])
                if self.drones[-1].distanceLeft > tripDistance:
                    self.drones[-1].trips.append(lastTrip)
                    self.drones[-1].distanceLeft -= tripDistance 
                else:
                    newDrone = Drone(lastTrip)
                    self.drones.append(newDrone)
                    newDrone.distanceLeft -= tripDistance

        for idx, drone in enumerate(self.drones[:numberOfDronesAtStart]):
            drone.battery = originalState_batteries[idx]
    
        
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

    def createTimeWindows(self): 
        
        for drone in self.drones:
            timeDelivered = 0 
            for trip in drone.trips: 
                for action in trip.actions[1:]: 
                    timeToCompleteAction = Node.distanceFinder(action.node, action.prevAction.node) // Parameters.droneSpeed
                    if "Delivery" in str(type(action)): 
                        lowerBound, upperBound = self.calculateTimeWindow(timeDelivered)
                        #since customer nodes can receive multiple deliveries, only set the open time to lower bound if it is null (as a previous delivery will have a ) 
                        if action.node.openTime == None:
                            action.node.openTime = lowerBound
                        else: 
                            action.node.openTime = min(action.node.openTime, lowerBound)
                        
                        if action.node.closeTime == None:
                            action.node.closeTime = upperBound
                        else: 
                            action.node.closeTime = max(action.node.closeTime, upperBound)
                    timeDelivered += timeToCompleteAction


                    
            
    '''
    Takes a time in seconds and returns a tuple with lower and upper bounds of the window
    '''
    def calculateTimeWindow(self, time):
        lowerBound = None 
        upperBound = None
        #drawing a uniform random variable as mean widens the crest of the normal curve to the bounds of the range
        mean = random.randint(0, Parameters.dayLength/4)
        halfRange = abs(math.floor(random.gauss(mean, Parameters.timeSlotStandardDev)))
        if time - halfRange < 0:
            lowerBound = 0
        else:
            lowerBound = time - halfRange
        
        if time + halfRange > Parameters.dayLength:
            upperBound = Parameters.dayLength
        else: 
            upperBound = time + halfRange
        #print(f"time: {time}, lowerBound: {lowerBound}, upperBound: {upperBound}")
        return int(lowerBound), int(upperBound)

    '''
    format: {number of drones used}(FOR EACH DRONE){number of trips in drone}(FOR EACH TRIP IN DRONE){number of actions in trip}{id of nodes visited in trip}{details of node visited either package delviered or battery dropped off/picked up}
    '''
    def createSolutionFile(self):
        outputElements = [] 
        outputElements.append(len(self.drones))
        for drone in self.drones: 
            #tools.drawDroneTrips(drone)
            outputElements.append(len(drone.trips))
            for trip in drone.trips: 
                outputElements.append(len(trip.actions))
                for action in trip.actions: 
                    outputElements.append(action.node.id)
                    #if action a deliver action add id of package delivered to solution file 
                    if (action.node.id) > 0 and (action.node.id <= self.noOfNodes):
                        outputElements.append(action.package.id)
                    elif "ChangeBattery" in str(type(action)): 
                        outputElements.append(action.batteryDropped)
                        outputElements.append(action.batterySelected)
                   
                    
        solutionString = ",".join([str(element) for element in outputElements])
        with open("solution.txt", "w") as file:
            file.seek(0)
            file.write(solutionString)

    '''
    Used for creating a file that allows the testing of the decoder in the genetic algorithm
    '''
    def createGenotype(self):
        outputElements = [] 
        for drone in self.drones: 
            for trip in drone.trips:
                for action in trip.actions: 
                    if "Delivery" in str(type(action)):
                        outputElements.append(action.package.id)
        
        solutionString = ",".join([str(element) for element in outputElements])
        with open("genotype.txt", "w") as file:
            file.seek(0)
            file.write(solutionString)

    '''
    format: {number of customers}{number of packages}{number of recharge stations}{depot coords and ids of batteries which start there}{customer coordinates with their time windows}{packages with id, weights and destination}{recharge stations and their respective starting batteries}
    All nodes, including charging nodes have an implied id val of their position in the problem file. Depot has id 0, first customer has id 1. The ids of recharging nodes continue after the packages, starting from noOfCustomers + 1
    '''
    def createProblemFile(self):
        stationsToMake = Parameters.noOfChargingStations - len(self.rechargeStations)
        for _ in range(stationsToMake):
            xCoord = random.randint(1, Parameters.citySize)
            yCoord = random.randint(1, Parameters.citySize)
            newStation = ChargingNode(xCoord, yCoord)
            newStation.batteriesHeld.append(Battery.createNew())
            self.rechargeStations.append(newStation)
        

        if len(self.rechargeStations) > Parameters.noOfChargingStations:
            chargingStationsWithOneBattery = list(filter(lambda x : len(x.batteriesHeld) == 1, self.rechargeStations))
            excess = len(chargingStationsWithOneBattery) - Parameters.noOfChargingStations 
            random.shuffle(chargingStationsWithOneBattery)
            for idx in range(excess):    
                self.rechargeStations.pop(self.rechargeStations.index(chargingStationsWithOneBattery[idx]))
            
        outputElements = [] 
        outputElements.append(max(Parameters.maxDrones, len(self.drones)))
        outputElements.append(Battery.idCounter - 1) #the solution does not implement any strategy for battery re-use. A new battery is created each time a drone visits a charging station. This means that the maximum batteries available in the problem is equal to this number 
        outputElements.append(self.noOfNodes) 
        outputElements.append(self.noOfPackages)
        outputElements.append(len(self.rechargeStations))
        outputElements.append(Depot()) #add depot to the problem string
        
        for customer in self.customers: 
            outputElements.append(customer)
        for package in self.packages: 
            outputElements.append(package)
            outputElements.append(package.destination.id)
        outputElements.append(Depot()) 
        outputElements.append(len(Depot.batteriesHeld))
        for battery in Depot.batteriesHeld:
            outputElements.append(battery)
        for rechargeStation in self.rechargeStations: 
            outputElements.append(rechargeStation)
            outputElements.append(len(rechargeStation.batteriesHeld))
            for battery in rechargeStation.batteriesHeld: #needs fixed - batteries held is ones held at the end not at start 
                outputElements.append(battery) 
            
        problemString = ",".join([str(element) for element in outputElements])
        with open("problem.txt", "w") as file: 
            file.seek(0)
            file.write(problemString)
        