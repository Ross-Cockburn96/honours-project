import random
import math
from node import CustomerNode, ChargingNode
import matplotlib.pyplot as plt
import parameters

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

