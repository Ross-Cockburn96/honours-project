import random
import parameters
import math
from drone import Drone 
from trip import Trip
from delivery import Delivery



class Solution:
    customers = [] #customers are represented by nodes 
    deliveries = [] #to be randomly allocated a delivery time and then distributed to trips
    drones = [] #trips are allocated to drones, a drone will have at least one trip 
    droneDeliveryAllocation = {} #dictionary containing temporary delivery assignment to drones (before trip construction)
    def __init__(self, customers): 
        self.customers = customers 

    def generate(self):
        numOfTrips = random.randint(1,parameters.customers) 
        numOfDrones = random.randint(1, numOfTrips)

        #not needed
        #trips = [Trip(Delivery(self.customers.pop(random.randrange(len(self.customers))))) for _ in range(numOfTrips)] #ensure that each trip has at least one delviery 
    
        #create deliveries for each customer (node) 
        self.deliveries = [Delivery(x) for x in self.customers]

        #assign random delivery time to each delivery
        for delivery in self.deliveries: 
            delivery.time = random.randint(parameters.minimumDeliveryTime, parameters.dayLength)
        
        #ensure each drone has at least one delivery
        for idx in range (numOfDrones):
            self.droneDeliveryAllocation[idx] = [self.deliveries[idx]]
        
        #populate rest of delivery assignment dictionary 
        for idx in range(numOfDrones, len(self.deliveries)):
            droneAllocation = random.randrange(numOfDrones)
            self.droneDeliveryAllocation[droneAllocation].append(self.deliveries[idx])

        
        for droneNo, assignedDeliveries in self.droneDeliveryAllocation.items():
            assignedDeliveries.sort(key=lambda x: x.time) #sort each drones deliveries so trips are in order
            
            #create trips within drone 
            trips = [] 
            while len(assignedDeliveries) > 0 :
                if parameters.droneCargoSlots > len(assignedDeliveries):
                    maxNumber = len(assignedDeliveries)
                else:
                    maxNumber = parameters.droneCargoSlots
                numberInTrip = random.randint(1,maxNumber) #randomly choose a number of packages to be in the trip, min = 1, max = cargoSize 
                trips.append(Trip(*assignedDeliveries[:numberInTrip]))
                del assignedDeliveries[:numberInTrip]
            self.drones.insert(droneNo, Drone(*trips))
    
    def getAllDeliveries(self): 
        deliveries = [delivery for drone in self.drones for trip in drone.trips for delivery in trip.deliveries]        
        return deliveries
    
    def getAllTrips(self):
        trips = [trip for drone in self.drones for trip in drone.trips]
        return trips

    def evaluate(self):
        return
    def __repr__(self):
        outputElements = []
        for drone in self.drones: 
            outputElements.append(len(drone.trips))
            for trip in drone.trips:
                outputElements.append(len(trip.deliveries))
                for delivery in trip.deliveries: 
                    outputElements.append(delivery.node.id)
                    outputElements.append(delivery.time)
            outputElements.append("\n")
        return ("".join([(str(x) + ", " if x != "\n" else "\n") for x in outputElements])) 

    