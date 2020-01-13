import random
import parameters
import math
from drone import Drone 
from trip import Trip
from delivery import Delivery



class Solution:
    customers = []
    drones = []

    def __init__(self, customers): 
        self.customers = customers 

    def generate(self):
        numOfTrips = random.randint(1,parameters.customers)
        numOfDrones = random.randint(1, numOfTrips)
        trips = [Trip(Delivery(self.customers.pop(random.randrange(len(self.customers))))) for _ in range(numOfTrips)] #ensure that each trip has at least one delviery 
        

        for customer in self.customers: 
            trip = trips[random.randrange(numOfTrips)]
            trip.addDelivery(Delivery(customer))

        self.drones = [Drone(trips.pop(random.randrange(len(trips)))) for _ in range(numOfDrones)] #ensure that each drone has at least one trip
        
        for trip in trips: 
            drone = self.drones[random.randrange(numOfDrones)]
            drone.addTrip(trip)

        for drone in self.drones: 
            minimumDeliveryTime = 0
            deliveriesRemaining = len(drone.getAllDeliveries())
            for trip in drone.trips:
                for delivery in trip.deliveries:
                    minimumDeliveryTime += 100
                    
                    #there should be at least 100 ms between drones so ensure there is enough time available for all delvieries to have the spread
                    maximumDeliveryTime = parameters.dayLength - (100 * deliveriesRemaining) 

                    #generates a random delivery time that is likely to be a smaller increment 
                    minimumDeliveryTime = math.floor(abs(random.random() - random.random()) *  (1 + maximumDeliveryTime - minimumDeliveryTime) + minimumDeliveryTime )
                    
                    deliveriesRemaining -= 1
                    delivery.time = minimumDeliveryTime

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

    