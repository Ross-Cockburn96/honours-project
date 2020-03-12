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
        random.seed(parameters.seed)

    def random(self, minVal, maxVal): 
        self.xCoord = random.randint(minVal, maxVal)
        self.yCoord = random.randint(minVal, maxVal)

    def getCoords(self): #returns a tuple for x and y coords 
        return self.xCoord, self.yCoord

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
        return math.floor(distance) #adds distance in meters to fitness function


    """
    calculates valid coordinates for the current node given the previous node in a trip and maximum distance (radius)
    """
    def randomValidCoord(self, prevNode, maxDistance):
        #print(f"previous node = {prevNode}, maxDistance = {maxDistance}")
        valid = False 
        while not valid: 
            r = maxDistance * math.sqrt(random.random())
            theta = random.random() * 2 * math.pi
            #print(prevNode.xCoord + r * math.cos(theta))
            x = math.floor(prevNode.xCoord + r * math.cos(theta))
            if x > parameters.citySizeMax: 
                continue
            if x < 0: 
                continue
            #print(prevNode.yCoord + r * math.sin(theta))
            y = math.floor(prevNode.yCoord + r * math.sin(theta))
            if y > parameters.citySizeMax:
                continue
            if y < 0: 
                continue
    
            valid = True
        self.xCoord = x
        self.yCoord = y
    

    
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
                candidates.append(sortedArray[r+1])
            else:
                candidates.insert(0, sortedArray[r-1])

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

    def __repr__(self):
        return str(self)

    def __str__(self):
        return (f"{self.xCoord}, {self.yCoord}, {self.openTime}, {self.closeTime}")

    #Overload less-than comparison operator for object (used in binary search) 
    def __lt__(self, other):
        if self.xCoord < other.xCoord:
            return True 
        elif self.xCoord == other.xCoord and self.yCoord < other.yCoord: 
            return True 
        else:
            return False 
    
    #Overload greater-than comparison operator for object (used in binary search) 
    def __gt__(self, other):
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
    
"""
Inherits from node, this object represents recharging stations. 
"""
class RechargeNode(Node): 
    def __init__(self, id= 0, xCoord = None, yCoord = None, capacity=None):
        super().__init__(id, xCoord, yCoord)
        self.capacity = capacity
    def __repr__(self):
        return str(self)

    def __str__(self):
        return (f"{self.xCoord}, {self.yCoord}, {self.capacity}")
'''
Inherits from node, this object represents depletion points and each object has a corresponding delivery.
The delivery is the delivery where the depletion point occured.
'''
class DepletionPoint(Node):
    def __init__(self, delivery, id=0, xCoord = None, yCoord = None):
        super().__init__(id, xCoord, yCoord)
        self.delivery = delivery