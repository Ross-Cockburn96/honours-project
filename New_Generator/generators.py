import random
import math
from generatorObjects.node import CustomerNode, ChargingNode, Node
import matplotlib.pyplot as plt
import parameters
from generatorObjects.drone import Drone 
from generatorObjects.action import Delivery, ChangeBattery, AtDepot
from generatorObjects.trip import Trip
from generatorObjects.package import Package 
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

    def generateRechargingStations(self): 
        numberOfStations = math.floor(parameters.rechargingNodetoCitySizeRatio * parameters.citySize)

        for _ in range(numberOfStations): 
            chargingStation = ChargingNode()
            chargingStation.random(0, self.citySize)
            x,y = chargingStation.getCoords()
            self.ax1.scatter(x,y, color='b')


    def generateTrips(self):
        customersCopy = self.customers.copy() #no deep copy required
        d1 = Drone()
        currentDrone = d1
        packagePool = self.noOfPackages
        packageCounter = 0 #used for assigning ids to packages
        while packagePool > 0:  
            
            packagesInTrip = random.randint(1,min(5, packagePool)) #decide how many packages the drone will deliver, limited by cargo hold size
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
            tripActions.insert(0, AtDepot())
            tripActions.append(AtDepot())

            orderedTripActions = tripActions[0] #depot
            orderedTrip = (self.nearestNeighbour([orderedTripActions], tripActions[1:]))

            trip = Trip(*orderedTrip) #creates trip object which forms the trip linked list 
            tools.drawTrip(trip)
            

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
        


            

        

