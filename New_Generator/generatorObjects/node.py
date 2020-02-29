import random
import parameters
import math

class Node: 
    xCoord = None
    yCoord = None 

    def random(self, minVal, maxVal): 
        self.xCoord = parameters.randomGen.randint(minVal, maxVal)
        self.yCoord = parameters.randomGen.randint(minVal, maxVal)

    def getCoords(self): 
        return self.xCoord, self.yCoord

    '''
    Given a center node and a radius, populates the coordinates at a random point within the circle 
    '''
    def randomWithinCircle(self, center, radius): 
    
        centerX, centerY = center.getCoords()

        valid = False 
        while not valid: 
            r = radius * math.sqrt(parameters.randomGen.random())
            theta = parameters.randomGen.random() * 2 * math.pi
            x = math.floor(centerX + r * math.cos(theta))
            if x > parameters.citySize:
                continue
            if x < 0:
                continue

            y = math.floor(centerY + r * math.sin(theta))
            if y > parameters.citySize:
                continue 
            if y < 0: 
                continue 
            
            valid = True 
        
        self.xCoord = x 
        self.yCoord = y 
        
    @classmethod
    def deepCopy(cls,node1, node2):
        node2.xCoord = node1.xCoord
        node2.yCoord = node1.yCoord

    '''
    Takes two nodes and returns the magnitude of their vector
    '''
    @classmethod
    def distanceFinder(cls, n1, n2):
        x1,y1 = n1.getCoords()
        x2,y2 = n2.getCoords()

        vecX = x2 - x1 
        vecY = y2 - y1 
    
        return math.sqrt(vecX**2 + vecY**2)
    def __repr__(self):
        return str(self)

    def __str__(self):
        return (f"{self.xCoord, self.yCoord}")    

class CustomerNode(Node): 
    def __init__(self):
        super().__init__()
        self.openTime = None
        self.closeTime = None
    
class ChargingNode(Node):
    def __init__(self):
        super().__init__()
        self.capacity = 0

class Depot(Node): 
    closeTime = parameters.dayLength
    openTime = 0
    def __init__(self):
        super().__init__()
        self.xCoord = 0
        self.yCoord = 0
        self.capacity = None
