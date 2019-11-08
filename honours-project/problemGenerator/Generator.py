import random
import math
from problemGenerator.Node import Node
import matplotlib.pyplot as plt

class Generator:
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

    nodes = []
    maxRange = 10
    rangeMultiplyer = 100
    def __init__(self, noOfNodes=10, noOfPackages=5 , nodemaxRangeRatio=.5, distribution="uniform" ):
        self.noOfNodes = noOfNodes
        self.noOfPackages = noOfPackages
        if not(distribution == "uniform" or distribution == "clustered"):
            print("distribution should be either 'uniform' or 'clustered' defaulting to uniform")
            distribution = "uniform"
        self.distribution = distribution
        if nodemaxRangeRatio <= 0: 
            nodemaxRangeRatio = 0.01
        self.nodemaxRangeRatio = nodemaxRangeRatio

    def uniformGeneration(self):
        for val in range(self.noOfNodes): 
            xCoord = random.randint(0, self.maxRange)
            yCoord = random.randint(0, self.maxRange)
            node = Node(xCoord, yCoord)
            self.nodes.append(node)
        
        fig, ax1 = plt.subplots(1,1)

        for node in self.nodes:
            x, y = node.str()
            ax1.set_xlim([0,150])
            ax1.set_ylim([0,150])
            ax1.scatter(x,y, alpha=0.8)
        
        plt.show()

    def clusteredGeneration(self):
        return None

    def generateNodes(self):
        upperLimit = 10
        self.maxRange = self.maxRange + math.floor(self.rangeMultiplyer * self.nodemaxRangeRatio)
        print (self.maxRange)

        if self.distribution == "uniform":
            self.uniformGeneration()
        else:
            self.clusteredGeneration()

    