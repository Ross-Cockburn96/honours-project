import random
from problemGenerator.Node import Node

class Generator:
    nodes = []

    def __init__(self, noOfNodes =10, noOfPackages=5 ):
        self.noOfNodes = noOfNodes
        self.noOfPackages = noOfPackages

    def generateNodes(self):
        upperLimit = 10
        for val in range(self.noOfNodes):
            xCoord = random.randint(0, 10)
            yCoord = random.randint(0, 10)
            node = Node(xCoord, yCoord)
            self.nodes.append(node)
        
        
