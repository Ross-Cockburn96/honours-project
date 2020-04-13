import random
from new_generator.parameters import Parameters 
import math

class Node: 
    xCoord = None
    yCoord = None 
    idCounter = 1
    def __init__(self):
        self.id = Node.idCounter
        Node.idCounter += 1

    def random(self, minVal, maxVal): 
        self.xCoord = Parameters.randomGen.randint(minVal, maxVal)
        self.yCoord = Parameters.randomGen.randint(minVal, maxVal)

    def getCoords(self): 
        return self.xCoord, self.yCoord

    '''
    Takes the centre of a circle, and the angle that angle of the arc and returns the arc star point coords and end point coords
    Destination is the customer node the drone is trying to get to but can't because of lack of battery 
    '''
    def calculateArcPoints(self, angle, circleCentre, midpoint):
        midX, midY = midpoint
        directionVector_X = midX - circleCentre.xCoord
        directionVector_Y = midY - circleCentre.yCoord

        theta1 = angle/2 
        theta2 = 360 - (angle/2) 
        #endPoint calc
        rotationalpoint1_X = round(circleCentre.xCoord + (directionVector_X * math.cos(math.radians(theta1)) - directionVector_Y * math.sin(math.radians(theta1))),3)
        rotationalpoint1_Y = round(circleCentre.yCoord + (directionVector_X * math.sin(math.radians(theta1)) + directionVector_Y * math.cos(math.radians(theta1))),3)

        #startPoint calc
        rotationalpoint2_X = round(circleCentre.xCoord + (directionVector_X * math.cos(math.radians(theta2)) - directionVector_Y * math.sin(math.radians(theta2))),3)
        rotationalpoint2_Y = round(circleCentre.yCoord + (directionVector_X * math.sin(math.radians(theta2)) + directionVector_Y * math.cos(math.radians(theta2))),3)
    
        return (rotationalpoint2_X,rotationalpoint2_Y),(rotationalpoint1_X, rotationalpoint1_Y)

    '''
    Takes the centre of a circle and the angle that the arc should make and returns if the Node is in the arc.
    Destination is the customer node the drone is trying to get to but can't because of lack of battery 
    '''
    def inArc(self, angle, circleCentre, midpoint):
        midX, midY = midpoint
        startPoint, endPoint = self.calculateArcPoints(angle, circleCentre, midpoint)
        xS, yS = startPoint
        xE, yE = endPoint 


        circleRadius = math.sqrt((midX - circleCentre.xCoord)**2 + (midY - circleCentre.yCoord)**2)
        distanceToPoint = math.sqrt((self.xCoord - circleCentre.xCoord)**2 + (self.yCoord - circleCentre.yCoord)**2)
        angleOfPoint = math.degrees(math.atan2(self.yCoord - circleCentre.yCoord, self.xCoord - circleCentre.xCoord))
        startingAngle = math.degrees(math.atan2(yS - circleCentre.yCoord, xS - circleCentre.xCoord))
        endingAngle = math.degrees(math.atan2(yE - circleCentre.yCoord, xE - circleCentre.xCoord))
        if distanceToPoint <= circleRadius:
            if startingAngle < endingAngle:
                if (angleOfPoint >= startingAngle) and (angleOfPoint <= endingAngle):
                    return True
            elif startingAngle > endingAngle:
                if angleOfPoint >= startingAngle:
                    return True
                elif angleOfPoint <= endingAngle:
                    return True
        return False

    '''
    Given a center node and a radius, populates the coordinates at a random point within the circle 
    '''
    def randomWithinCircle(self, center, radius): 
    
        centerX, centerY = center.getCoords()

        valid = False 
        while not valid: 
            r = radius * math.sqrt(Parameters.randomGen.random())
            theta = Parameters.randomGen.random() * 2 * math.pi
            x = math.floor(centerX + r * math.cos(theta))
            if x > Parameters.citySize:
                continue
            if x < 0:
                continue

            y = math.floor(centerY + r * math.sin(theta))
            if y > Parameters.citySize:
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
    takes two nodes and returns the unit vector
    '''
    @classmethod
    def calculateUnitVector(cls, n1, n2):
        vx = n2.xCoord - n1.xCoord 
        vy = n2.yCoord - n1.yCoord 

        magnitude = math.sqrt(vx**2 + vy**2)
        unitx = vx/magnitude
        unity = vy/magnitude

        return unitx, unity
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
        if other == None: 
            return False
        if self.xCoord == other.xCoord and self.yCoord == other.yCoord:
            return True 
        else:
            return False 
    
    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"{self.xCoord},{self.yCoord}"  


class CustomerNode(Node): 
    def __init__(self, openTime, closeTime):
        super().__init__()
        self.closeTime = closeTime
        self.openTime = openTime

    @classmethod
    def createNew(cls):
        lower = random.randint(0,Parameters.dayLength)
        upper = random.randint(lower, Parameters.dayLength)
        return cls(lower, upper)
    
    @classmethod
    def rebuild(cls, x, y,openTime, closeTime):
        node = cls(openTime, closeTime)
        node.xCoord= x
        node.yCoord =y
        return node

    def __repr__(self):
        return str(self)
    
    def __str__(self):
        return f"{super().__str__()},{self.openTime},{self.closeTime}"

'''
A charging station, this has coordinates and can be visited by a drone to switch out batteries 
The batteriesheld variable is a list of batteries that the node should have at the start 
'''
class ChargingNode(Node):
    def __init__(self, xCoord, yCoord):
        super().__init__()
        self.id += 1 #plus one because first charging station id is reserved for depot charging station
        self.xCoord = xCoord
        self.yCoord = yCoord
        self.batteriesHeld = []
        self.capacity = 0

class DepletionPoint(Node):
    def __init__(self, action, drone, batteryUsed, trip, xCoord, yCoord): 
        super().__init__()
        self.id = None
        Node.idCounter -= 1 
        self.xCoord = xCoord
        self.yCoord = yCoord
        self.drone = drone #drone that was depleted
        self.batteryUsed = batteryUsed
        self.trip = trip #trip that action was on
        self.action = action #the action that was being carried out when the charge depletion occured 

class Depot(Node): 
    closeTime = Parameters.dayLength
    openTime = 0
    batteriesHeld = []
    capacity = 0
    def __init__(self):
        super().__init__()
        self.id = 0 
        Node.idCounter -= 1
        self.xCoord = 0
        self.yCoord = 0

    def __repr__(self):
        return str(self)
    
    def __str__(self):
        return f"{self.xCoord},{self.yCoord}"
