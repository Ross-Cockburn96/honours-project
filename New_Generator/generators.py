import random
import math
from node import Node
import matplotlib.pyplot as plt
import parameters

class Problem:
    """ 
    This class is used to generate random problems to the 
    Multiple Knapsack Problem for Package Delivery Drones 
    
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

    clusterToRangeRatio = .25
    clusterDeviationFromPoint = 5
    def __init__(self, noOfNodes, noOfPackages, distribution="uniform" ):
        self.nodes = []
        self.citySize = parameters.citySize 
        self.noOfNodes = noOfNodes
        self.noOfPackages = noOfPackages
        if not(distribution == "uniform" or distribution == "clustered"):
            print("distribution should be either 'uniform' or 'clustered' defaulting to uniform")
            distribution = "uniform"
        self.distribution = distribution

    def uniformGeneration(self):
        for _ in range(self.noOfNodes): 
            node = Node()
            node.random(0, self.citySize+1)
            self.nodes.append(node)
        
        fig, ax1 = plt.subplots(1,1)

        for node in self.nodes:
            x, y = node.getCoords()
            ax1.set_xlim([0,150])
            ax1.set_ylim([0,150])
            ax1.scatter(x,y, alpha=0.8)
        
        plt.show()



    def createClusterCenters(self):
        numberOfClusters = math.floor(self.citySize * parameters.clusterToCitySizeRatio)
        clusterCenters = []
        for _ in range(numberOfClusters):
            cluster = Node() 
            cluster.random(0, self.citySize + 1)
            clusterCenters.append(cluster)
            self.nodes.append(cluster)
        return clusterCenters


    def clusteredGeneration(self):
        clusterCenters = self.createClusterCenters()
        for _ in range(self.noOfNodes): 
            node = Node() #create customer node
            clusterIndex = random.randint(0, len(clusterCenters) - 1 ) #decide which cluster this node will belong 
            node.randomWithinCircle(clusterCenters[clusterIndex], 500)
            self.nodes.append(node)

        fig, ax1 = plt.subplots(1,1)
        for node in self.nodes:
            x,y = node.str()
            ax1.set_xlim([0,150])
            ax1.set_ylim([0,150])
            ax1.scatter(x,y, alpha=0.8)
        
        plt.show()


    def generateNodes(self):
        if self.distribution == "uniform":
            self.uniformGeneration()
        else:
            self.clusteredGeneration()


