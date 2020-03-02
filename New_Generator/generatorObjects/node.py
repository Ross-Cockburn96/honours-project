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
        return math.floor(distance) #adds distance in meters to fitness function
        
    @classmethod
    def deepCopy(cls,node1, node2):
        node2.xCoord = node1.xCoord
        node2.yCoord = node1.yCoord

    '''
    Takes a sorted array of elements and returns the index of the searchVal.
    If the searchVal cannot be found, the index of the closes value is returned.
    '''
    @classmethod
    def binarySearch(cls, sortedArray, l, r, searchVal):
        if r >= l:
            mid = l + (r - l) // 2
            # If element is present at the middle itself 
            
            if sortedArray[mid] == searchVal: 
                return mid 
            
            # If element is smaller than mid, then it  
            # can only be present in left subarray 
            elif sortedArray[mid] > searchVal: 
                return cls.binarySearch(sortedArray, l, mid-1, searchVal) 
    
            # Else the element can only be present  
            # in right subarray 
            else: 
                return cls.binarySearch(sortedArray, mid + 1, r, searchVal) 
        
        else:
            #list of potentially closest charging points
            candidates = [sortedArray[r]] 

            #these are rough methods of minimising the candidate list size to sensible candidates 
            if r > 0 and r < len(sortedArray)-1: 
                candidates.insert(0, sortedArray[r-1])
                candidates.append(sortedArray[r+1])
            elif r==0 or r==-1:  
                candidates.append(sortedArray[r+1], sortedArray[r+2])
            else:
                candidates.insert(0, sortedArray[r-1], sortedArray[r+1])
            print(candidates)
            #creates a list of magnitutes from the distance vectors from searchVal to each of the candidates 
            candidateVectorMags = list(map(cls.distanceFinder, candidates, [searchVal]*len(candidates))) 

            #returns the candidate that is closest in distance to the search value 
            return candidates[candidateVectorMags.index(min(candidateVectorMags))]
    
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


    #Overload less-than comparison operator for object (used in binary search) 
    def __lt__(self, other):
        print(f"{self} less than {other}")
        if self.xCoord < other.xCoord:
            return True 
        elif self.xCoord == other.xCoord and self.yCoord < other.yCoord: 
            return True 
        else:
            return False 
    
    #Overload greater-than comparison operator for object (used in binary search) 
    def __gt__(self, other):
        print(f"{self} greater than {other}")
        if self.xCoord > other.xCoord:
            return True 
        elif self.xCoord == other.xCoord and self.yCoord > other.yCoord: 
            return True 
        else:
            return False 

    #Overload equals comparison operator for object (used in binary search)
    def __eq__(self, other):
        if self.xCoord == other.xCoord and self.yCoord == other.yCoord:
            return True 
        else:
            return False 
    
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
    def __init__(self, xCoord, yCoord):
        super().__init__()
        self.xCoord = xCoord
        self.yCoord = yCoord
        self.batteriesHeld = []
        self.capacity = 0

class DepletionPoint(Node):
    def __init__(self, action, drone, trip, xCoord, yCoord): 
        super().__init__()
        self.xCoord = xCoord
        self.yCoord = yCoord
        self.drone = drone #drone that was depleted
        self.trip = trip #trip that action was on
        self.action = action #the action that was being carried out when the charge depletion occured 

class Depot(Node): 
    closeTime = parameters.dayLength
    openTime = 0
    batteriesHeld = []
    capacity = 0
    def __init__(self):
        super().__init__()
        self.xCoord = 0
        self.yCoord = 0
