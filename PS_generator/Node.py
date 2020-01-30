import random
import math
import parameters


#Nodes either represent customers or the depot 
class Node:

    def __init__(self, id=0, xCoord = None, yCoord = None):
        self.openTime = 0 
        self.closeTime = 0
        self.id = id
        self.xCoord = xCoord #km
        self.yCoord = yCoord #km

    def random(self, minVal, maxVal): 
        self.xCoord = random.randint(minVal, maxVal)
        self.yCoord = random.randint(minVal, maxVal)

    @classmethod
    def deepCopy(cls,node1, node2):
        node2.xCoord = node1.xCoord
        node2.yCoord = node1.yCoord
    

    """
    Takes any number of nodes as argument and returns the distance of the route.
    Assumes that the order the nodes are in is the order of the path.
    """
    @classmethod
    def distanceCalc(cls, *args):
        nodes = list(args)
        #print(f"considering nodes {str(nodes)}")
        numOfNodes = len(nodes)
        distance = 0
        for idx, node in enumerate(nodes):
            if idx == (numOfNodes-1):
                break
            #print(f"idx is {idx} num of nodes is {numOfNodes}")
            nextNode = nodes[idx + 1]
            distance += math.sqrt(((node.xCoord - nextNode.xCoord)**2) + ((node.yCoord - nextNode.yCoord)**2))
        #print(f"distance is {distance}")
        return math.floor(distance * parameters.unit) #adds distance in meters to fitness function


    """
    calculates valid coordinates for the current node given the previous node in a trip and maximum distance (radius)
    """
    def randomValidCoord(self, prevNode, maxDistance):
        print(f"previous node = {prevNode}, maxDistance = {maxDistance}")
        r = maxDistance * math.sqrt(random.random())
        theta = random.random() * 2 * math.pi
        print(prevNode.xCoord + r * math.cos(theta))
        x = math.floor(prevNode.xCoord + r * math.cos(theta))
        if x > parameters.citySizeMax: 
            x = parameters.citySizeMax
        if x < 0: 
            x = 0
        print(prevNode.yCoord + r * math.sin(theta))
        y = math.floor(prevNode.yCoord + r * math.sin(theta))
        if y > parameters.citySizeMax:
            y = parameters.citySizeMax
        if y < 0: 
            y = 0
        self.xCoord = x
        self.yCoord = y
        print(f"valid x is {x}, valid y is {y}")

    def __repr__(self):
        return str(self)

    def __str__(self):
        return (f"{self.xCoord}, {self.yCoord}, {self.openTime}, {self.closeTime}")
