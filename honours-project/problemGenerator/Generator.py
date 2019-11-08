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

    Methods 
    -------
    generateNodes()
        randomly generates the number of nodes specified by noOfNodes attribute
    """

    nodes = []
    maxRange = 10
    rangeMultiplyer = 50
    def __init__(self, noOfNodes=10, noOfPackages=5 , nodemaxRangeRatio=.5 ):
        self.noOfNodes = noOfNodes
        self.noOfPackages = noOfPackages
        if nodemaxRangeRatio <= 0: 
            nodemaxRangeRatio = 0.01
        self.nodemaxRangeRatio = nodemaxRangeRatio


    
    def generateNodes(self):
        upperLimit = 10
        self.maxRange = self.maxRange + (self.rangeMultiplyer * self.nodemaxRangeRatio)
        print (self.maxRange)

        for val in maxRange(self.noOfNodes): 
            xCoord = random.randint(0, self.maxRange)
            yCoord = random.randint(0, self.maxRange)
            node = Node(xCoord, yCoord)
            self.nodes.append(node)
        
        fig, ax1 = plt.subplots(1,1)

        for node in self.nodes:
            x, y = node.str()
            ax1.set_xlim([0,500])
            ax1.set_ylim([0,500])
            ax1.scatter(x,y, alpha=0.8)
        
        plt.show()
        
