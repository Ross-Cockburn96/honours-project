import random
import math
from problemGenerator.Node import Node
import matplotlib.pyplot as plt

class Generator:
    nodes = []
    nodeCoordLimit = 10
    maxDensity = 5
    def __init__(self, noOfNodes =10, noOfPackages=5, nodeDensity=1):
        self.noOfNodes = noOfNodes
        self.noOfPackages = noOfPackages
        self.nodeDensity = nodeDensity


    def generateNodes(self):
        upperLimit = 10
        origNodes = []
        for val in range(self.noOfNodes):
            density = math.floor(self.maxDensity * self.nodeDensity) + 1
            print(f"density is {density}")
            xCoord = random.randint(0, self.nodeCoordLimit)
            xCoordOrig = xCoord
            xCoord = xCoord * density

            yCoord = random.randint(0, self.nodeCoordLimit)
            yCoordOrig = yCoord
            yCoord = yCoord * density

            origNodes.append(Node(xCoordOrig, yCoordOrig))
            node = Node(xCoord, yCoord)
            self.nodes.append(node)
        
        fig, (ax1, ax2) = plt.subplots(1,2)

        for node in self.nodes:
            x, y = node.str()
            ax1.set_xlim([0,25])
            ax1.set_ylim([0,25])
            ax1.scatter(x,y, alpha=0.8)
        
        for node in origNodes:
            x,y = node.str()
            ax2.set_xlim([0,25])
            ax2.set_ylim([0,25])
            ax2.scatter(x,y, alpha=0.8)
        plt.show()
        
