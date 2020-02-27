import random
import parameters
import math

class Node: 
    xCoord = None
    yCoord = None 

    def random(self, minVal, maxVal): 
        self.xCoord = random.randint(minVal, maxVal)
        self.yCoord = random.randint(minVal, maxVal)

    def getCoords(self): 
        return self.xCoord, self.yCoord

    '''
    Given a center node and a radius, populates the coordinates at a random point within the circle 
    '''
    def randomWithinCircle(self, center, radius): 
    
        centerX, centerY = center.getCoords()

        valid = False 
        while not valid: 
            r = radius * math.sqrt(random.random())
            theta = random.random() * 2 * math.pi
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

    
    def __str__(self):
        return (f"{self.xCoord, self.yCoord}")    

class CustomerNode(Node): 
    def __init__(self):
        super().__init__()
    
class ChargingNode(Node):
    def __init__(self):
        super().__init__()
        self.capacity = 0
