import random
import math
from problemGenerator.Node import Node
import matplotlib.pyplot as plt

class Generator:
    nodes = []
    nodeCoordLimit = 10
    maxRange = 50
    def __init__(self, noOfNodes =10, noOfPackages=5, nodeRange=.5):
        self.noOfNodes = noOfNodes
        self.noOfPackages = noOfPackages
        if nodeRange <= 0: 
            nodeRange = 0.01
        self.nodeRange = nodeRange


    def generateNodes(self):
        upperLimit = 10
        self.nodeCoordLimit = self.nodeCoordLimit * self.maxRange * self.nodeRange
        print (self.nodeCoordLimit)

        for val in range(self.noOfNodes): 
            #density = math.floor(self.maxRange * self.nodeRange) + 1
            xCoord = random.randint(0, self.nodeCoordLimit)
            yCoord = random.randint(0, self.nodeCoordLimit)

            node = Node(xCoord, yCoord)
            self.nodes.append(node)
        
        fig, ax1 = plt.subplots(1,1)

        for node in self.nodes:
            x, y = node.str()
            ax1.set_xlim([0,500])
            ax1.set_ylim([0,500])
            ax1.scatter(x,y, alpha=0.8)
        
        plt.show()
        
