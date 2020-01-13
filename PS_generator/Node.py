import random
import math
import parameters

class Node:
    xCoord = 0 #km
    yCoord = 0  #km
    openTime = 0 
    closeTime = 0

    def __init__(self, id):
        self.id = id

    def random(self, minVal, maxVal): 
        self.xCoord = random.randint(minVal, maxVal)
        self.yCoord = random.randint(minVal, maxVal)

    @classmethod
    def deepCopy(cls,node1, node2):
        node2.xCoord = node1.xCoord
        node2.yCoord = node1.yCoord
    
    def randomValidCoord(self, prevNode, maxDistance):
        print(maxDistance)
        r = maxDistance * math.sqrt(random.random())
        theta = random.random() * 2 * math.pi
        x = math.floor(prevNode.xCoord + r * math.cos(theta))
        if x > parameters.citySizeMax: 
            x = parameters.citySizeMax
        if x < 0: 
            x = 0
        y = math.floor(prevNode.yCoord + r * math.sin(theta))
        if y > parameters.citySizeMax:
            y = parameters.citySizeMax
        if y < 0: 
            y = 0
        self.xCoord = x
        self.yCoord = y
    
    def __str__(self):
        return (f"{self.xCoord}, {self.yCoord}, {self.openTime}, {self.closeTime}")

        